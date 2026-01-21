from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime

from coze_coding_dev_sdk.database import Base

# ==================== 商品表 ====================
class Product(Base):
    """商品表 - 存储图书商品信息"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, comment="商品ID")
    isbn = Column(String(20), unique=True, nullable=False, index=True, comment="ISBN编号")
    name = Column(String(255), nullable=False, comment="图书名称")
    author = Column(String(128), nullable=False, comment="作者")
    publisher = Column(String(128), nullable=False, comment="出版社")
    publish_date = Column(Date, nullable=True, comment="出版日期")
    category = Column(String(100), nullable=True, comment="图书分类")
    price = Column(Numeric(10, 2), nullable=False, comment="销售价格")
    cost = Column(Numeric(10, 2), nullable=True, comment="采购成本")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, comment="供应商ID")
    description = Column(Text, nullable=True, comment="图书描述")
    barcode = Column(String(50), unique=True, nullable=True, index=True, comment="条形码")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否上架")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    supplier = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

    __table_args__ = (
        Index("ix_products_category", "category"),
        Index("ix_products_isbn", "isbn"),
    )


# ==================== 库存表 ====================
class Inventory(Base):
    """库存表 - 存储库存数量和预警信息"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, comment="库存ID")
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False, index=True, comment="商品ID")
    quantity = Column(Integer, nullable=False, default=0, comment="当前库存数量")
    min_stock_threshold = Column(Integer, nullable=False, default=10, comment="最小库存阈值（低于此值触发预警）")
    max_stock_threshold = Column(Integer, nullable=True, comment="最大库存阈值（高于此值提醒积压）")
    reorder_quantity = Column(Integer, nullable=True, default=50, comment="建议补货数量")
    last_restock_date = Column(DateTime(timezone=True), nullable=True, comment="最后补货时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    product = relationship("Product", back_populates="inventory")

    __table_args__ = (
        Index("ix_inventory_product_id", "product_id"),
    )


# ==================== 供应商表 ====================
class Supplier(Base):
    """供应商表 - 存储供应商信息"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, comment="供应商ID")
    name = Column(String(255), nullable=False, comment="供应商名称")
    contact_person = Column(String(128), nullable=True, comment="联系人")
    phone = Column(String(50), nullable=True, comment="联系电话")
    email = Column(String(255), nullable=True, comment="邮箱")
    address = Column(Text, nullable=True, comment="地址")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    products = relationship("Product", back_populates="supplier")


# ==================== 客户表 ====================
class Customer(Base):
    """客户表 - 存储客户信息"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, comment="客户ID")
    name = Column(String(128), nullable=False, comment="客户姓名")
    phone = Column(String(50), nullable=True, comment="联系电话")
    email = Column(String(255), nullable=True, comment="邮箱")
    level = Column(String(50), default="普通会员", nullable=False, comment="会员等级")
    points = Column(Integer, default=0, nullable=False, comment="积分")
    total_purchase = Column(Numeric(12, 2), default=0, nullable=False, comment="累计消费金额")
    last_purchase_date = Column(DateTime(timezone=True), nullable=True, comment="最后购买时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    orders = relationship("Order", back_populates="customer")


# ==================== 订单表 ====================
class Order(Base):
    """订单表 - 存储销售订单信息"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, comment="订单ID")
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True, comment="客户ID")
    total_amount = Column(Numeric(12, 2), nullable=False, comment="订单总金额")
    status = Column(String(50), default="pending", nullable=False, comment="订单状态: pending/paid/shipped/completed/cancelled")
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ==================== 订单明细表 ====================
class OrderItem(Base):
    """订单明细表 - 存储订单商品明细"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, comment="明细ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    subtotal = Column(Numeric(12, 2), nullable=False, comment="小计")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )


# ==================== 库存预警记录表 ====================
class StockAlert(Base):
    """库存预警记录表 - 记录库存预警历史"""
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, comment="预警ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True, comment="商品ID")
    alert_type = Column(String(50), nullable=False, comment="预警类型: low_stock/overstock")
    current_quantity = Column(Integer, nullable=False, comment="当前库存")
    threshold_value = Column(Integer, nullable=False, comment="阈值")
    suggested_reorder_quantity = Column(Integer, nullable=True, comment="建议补货数量")
    alert_status = Column(String(50), default="pending", nullable=False, comment="处理状态: pending/processed/ignored")
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="处理时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    __table_args__ = (
        Index("ix_stock_alerts_product_id", "product_id"),
        Index("ix_stock_alerts_created_at", "created_at"),
    )
