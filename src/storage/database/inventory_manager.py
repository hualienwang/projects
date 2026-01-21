from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Inventory, Product, StockAlert


# --- Pydantic Models ---
class InventoryCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(default=0, description="当前库存数量")
    min_stock_threshold: int = Field(default=10, description="最小库存阈值")
    max_stock_threshold: Optional[int] = Field(None, description="最大库存阈值")
    reorder_quantity: Optional[int] = Field(default=50, description="建议补货数量")


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_stock_threshold: Optional[int] = None
    max_stock_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None


class StockAlertCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    alert_type: str = Field(..., description="预警类型: low_stock/overstock")
    current_quantity: int = Field(..., description="当前库存")
    threshold_value: int = Field(..., description="阈值")
    suggested_reorder_quantity: Optional[int] = Field(None, description="建议补货数量")


class StockAlertUpdate(BaseModel):
    alert_status: str = Field(..., description="处理状态: pending/processed/ignored")


# --- Manager Class ---
class InventoryManager:
    """Manager class for Inventory operations using Pydantic models for validation."""

    def create_inventory(self, db: Session, inventory_in: InventoryCreate) -> Inventory:
        """创建库存记录"""
        inventory_data = inventory_in.model_dump()
        db_inventory = Inventory(**inventory_data)
        db.add(db_inventory)
        try:
            db.commit()
            db.refresh(db_inventory)
            return db_inventory
        except Exception:
            db.rollback()
            raise

    def get_inventory_by_id(self, db: Session, inventory_id: int) -> Optional[Inventory]:
        """根据ID获取库存记录"""
        return db.query(Inventory).filter(Inventory.id == inventory_id).first()

    def get_inventory_by_product_id(self, db: Session, product_id: int) -> Optional[Inventory]:
        """根据商品ID获取库存记录"""
        return db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def get_all_inventory(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        low_stock_only: bool = False
    ) -> List[Dict]:
        """获取所有库存记录"""
        query = db.query(
            Inventory.id,
            Inventory.product_id,
            Inventory.quantity,
            Inventory.min_stock_threshold,
            Inventory.max_stock_threshold,
            Inventory.reorder_quantity,
            Inventory.last_restock_date,
            Product.isbn,
            Product.name,
            Product.author,
            Product.category,
            Product.price
        ).join(
            Product, Inventory.product_id == Product.id
        )

        if low_stock_only:
            query = query.filter(Inventory.quantity < Inventory.min_stock_threshold)

        results = query.offset(skip).limit(limit).all()
        return [
            {
                "id": r.id,
                "product_id": r.product_id,
                "isbn": r.isbn,
                "name": r.name,
                "author": r.author,
                "category": r.category,
                "price": float(r.price),
                "quantity": r.quantity,
                "min_stock_threshold": r.min_stock_threshold,
                "max_stock_threshold": r.max_stock_threshold,
                "reorder_quantity": r.reorder_quantity,
                "last_restock_date": r.last_restock_date.isoformat() if r.last_restock_date else None
            }
            for r in results
        ]

    def update_inventory(
        self,
        db: Session,
        product_id: int,
        inventory_in: InventoryUpdate
    ) -> Optional[Inventory]:
        """更新库存信息"""
        db_inventory = self.get_inventory_by_product_id(db, product_id)
        if not db_inventory:
            return None
        update_data = inventory_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_inventory, field):
                setattr(db_inventory, field, value)
        db.add(db_inventory)
        try:
            db.commit()
            db.refresh(db_inventory)
            return db_inventory
        except Exception:
            db.rollback()
            raise

    def adjust_inventory_quantity(
        self,
        db: Session,
        product_id: int,
        delta: int
    ) -> Optional[Inventory]:
        """调整库存数量（增加或减少）"""
        db_inventory = self.get_inventory_by_product_id(db, product_id)
        if not db_inventory:
            return None

        new_quantity = db_inventory.quantity + delta
        if new_quantity < 0:
            raise ValueError("库存数量不能为负数")

        db_inventory.quantity = new_quantity
        db.add(db_inventory)
        try:
            db.commit()
            db.refresh(db_inventory)
            return db_inventory
        except Exception:
            db.rollback()
            raise

    def check_low_stock(self, db: Session) -> List[Dict]:
        """检查所有低库存商品"""
        query = db.query(
            Inventory.id,
            Inventory.product_id,
            Inventory.quantity,
            Inventory.min_stock_threshold,
            Inventory.reorder_quantity,
            Product.isbn,
            Product.name,
            Product.author,
            Product.publisher,
            Product.price
        ).join(
            Product, Inventory.product_id == Product.id
        ).filter(
            Inventory.quantity < Inventory.min_stock_threshold
        )

        results = query.all()
        return [
            {
                "inventory_id": r.id,
                "product_id": r.product_id,
                "isbn": r.isbn,
                "name": r.name,
                "author": r.author,
                "publisher": r.publisher,
                "price": float(r.price),
                "current_quantity": r.quantity,
                "min_threshold": r.min_stock_threshold,
                "reorder_quantity": r.reorder_quantity,
                "shortage": r.min_stock_threshold - r.quantity
            }
            for r in results
        ]

    def check_overstock(self, db: Session) -> List[Dict]:
        """检查所有库存积压商品"""
        query = db.query(
            Inventory.id,
            Inventory.product_id,
            Inventory.quantity,
            Inventory.max_stock_threshold,
            Product.isbn,
            Product.name,
            Product.author,
            Product.price
        ).join(
            Product, Inventory.product_id == Product.id
        ).filter(
            Inventory.max_stock_threshold.isnot(None),
            Inventory.quantity > Inventory.max_stock_threshold
        )

        results = query.all()
        return [
            {
                "inventory_id": r.id,
                "product_id": r.product_id,
                "isbn": r.isbn,
                "name": r.name,
                "author": r.author,
                "price": float(r.price),
                "current_quantity": r.quantity,
                "max_threshold": r.max_stock_threshold,
                "overstock": r.quantity - r.max_stock_threshold
            }
            for r in results
        ]

    def create_stock_alert(self, db: Session, alert_in: StockAlertCreate) -> StockAlert:
        """创建库存预警记录"""
        alert_data = alert_in.model_dump()
        db_alert = StockAlert(**alert_data)
        db.add(db_alert)
        try:
            db.commit()
            db.refresh(db_alert)
            return db_alert
        except Exception:
            db.rollback()
            raise

    def get_pending_alerts(self, db: Session, limit: int = 100) -> List[StockAlert]:
        """获取待处理的预警记录"""
        return db.query(StockAlert).filter(
            StockAlert.alert_status == "pending"
        ).order_by(
            StockAlert.created_at.desc()
        ).limit(limit).all()

    def update_alert_status(
        self,
        db: Session,
        alert_id: int,
        status_update: StockAlertUpdate
    ) -> Optional[StockAlert]:
        """更新预警状态"""
        db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
        if not db_alert:
            return None

        db_alert.alert_status = status_update.alert_status
        if status_update.alert_status != "pending":
            db_alert.processed_at = datetime.now()

        db.add(db_alert)
        try:
            db.commit()
            db.refresh(db_alert)
            return db_alert
        except Exception:
            db.rollback()
            raise
