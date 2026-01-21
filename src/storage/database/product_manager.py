from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from storage.database.shared.model import Product


# --- Pydantic Models ---
class ProductCreate(BaseModel):
    isbn: str = Field(..., description="ISBN编号")
    name: str = Field(..., description="图书名称")
    author: str = Field(..., description="作者")
    publisher: str = Field(..., description="出版社")
    publish_date: Optional[str] = Field(None, description="出版日期")
    category: Optional[str] = Field(None, description="图书分类")
    price: float = Field(..., description="销售价格")
    cost: Optional[float] = Field(None, description="采购成本")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    description: Optional[str] = Field(None, description="图书描述")
    barcode: Optional[str] = Field(None, description="条形码")


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None


class ProductFilter(BaseModel):
    category: Optional[str] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None  # 搜索名称、作者或ISBN


# --- Manager Class ---
class ProductManager:
    """Manager class for Product operations using Pydantic models for validation."""

    def create_product(self, db: Session, product_in: ProductCreate) -> Product:
        """创建新商品"""
        product_data = product_in.model_dump()
        db_product = Product(**product_data)
        db.add(db_product)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception:
            db.rollback()
            raise

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        """根据ID获取商品"""
        return db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_isbn(self, db: Session, isbn: str) -> Optional[Product]:
        """根据ISBN获取商品"""
        return db.query(Product).filter(Product.isbn == isbn).first()

    def get_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        product_filter: Optional[ProductFilter] = None
    ) -> List[Product]:
        """获取商品列表"""
        query = db.query(Product)

        if product_filter:
            if product_filter.category:
                query = query.filter(Product.category == product_filter.category)
            if product_filter.supplier_id:
                query = query.filter(Product.supplier_id == product_filter.supplier_id)
            if product_filter.is_active is not None:
                query = query.filter(Product.is_active == product_filter.is_active)
            if product_filter.search:
                search_pattern = f"%{product_filter.search}%"
                query = query.filter(
                    (Product.name.ilike(search_pattern)) |
                    (Product.author.ilike(search_pattern)) |
                    (Product.isbn.ilike(search_pattern))
                )

        return query.offset(skip).limit(limit).all()

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_in: ProductUpdate
    ) -> Optional[Product]:
        """更新商品信息"""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_product, field):
                setattr(db_product, field, value)
        db.add(db_product)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception:
            db.rollback()
            raise

    def delete_product(self, db: Session, product_id: int) -> bool:
        """删除商品"""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return False
        try:
            db.delete(db_product)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise

    def get_low_stock_products(self, db: Session, threshold: int) -> List[dict]:
        """获取库存低于阈值的商品（关联库存表查询）"""
        query = db.query(
            Product.id,
            Product.isbn,
            Product.name,
            Product.author,
            Product.price,
            Product.category
        ).join(
            Product.inventory
        ).filter(
            Inventory.quantity < threshold
        )
        results = query.all()
        return [
            {
                "id": r.id,
                "isbn": r.isbn,
                "name": r.name,
                "author": r.author,
                "price": float(r.price),
                "category": r.category
            }
            for r in results
        ]


# 避免循环导入，在文件末尾导入Inventory
from storage.database.shared.model import Inventory
