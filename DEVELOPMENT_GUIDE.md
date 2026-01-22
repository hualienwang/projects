# 瓊林圖書事業有限公司 - 開發實施指南

## 概述

本指南提供了瓊林圖書事業有限公司進銷存/客戶管理/POS系統整合專案的詳細開發實施步驟。按照此指南，開發團隊可以逐步實現專案目標，確保系統的完整性和一致性。

## 開發環境設置

### 系統要求
- Node.js v18+ (後端開發)
- Python 3.9+ (現有系統部分)
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose
- Git

### 初始化專案結構
```bash
/workspace/
├── backend/                 # 後端服務 (Node.js)
│   ├── pos-service/         # POS服務
│   ├── inventory-service/   # 庫存服務
│   ├── crm-service/         # CRM服務
│   ├── report-service/      # 報表服務
│   └── api-gateway/         # API閘道
├── frontend/                # 前端應用
│   ├── pos-app/             # POS前端 (Electron)
│   ├── web-admin/           # Web管理後台 (React)
│   └── mobile-app/          # 移動端 (React Native/PWA)
├── shared/                  # 共享元件
│   ├── models/              # 資料模型
│   ├── utils/               # 工具函數
│   └── config/              # 配置文件
├── docker/                  # Docker配置
├── docs/                    # 文件
└── tests/                   # 測試文件
```

### 安裝依賴
```bash
# 安裝全域工具
npm install -g @nestjs/cli
npm install -g electron
npm install -g nodemon

# 初始化後端專案
mkdir backend && cd backend
nest new pos-service
nest new inventory-service
nest new crm-service
nest new report-service
nest new api-gateway

# 初始化前端專案
mkdir frontend && cd frontend
npx create-react-app web-admin
cd web-admin && npm install antd @ant-design/icons redux react-redux @reduxjs/toolkit axios chart.js react-chartjs-2
```

## 後端服務開發

### 1. POS服務 (pos-service)

#### 安裝依賴
```bash
cd backend/pos-service
npm install @nestjs/websockets @nestjs/platform-socket.io @nestjs/typeorm typeorm pg class-validator class-transformer
npm install --save-dev @types/socket.io
```

#### 建立POS控制器
```typescript
// src/pos/pos.controller.ts
import { Controller, Post, Get, Body, Param, HttpCode, HttpStatus } from '@nestjs/common';
import { PosService } from './pos.service';
import { CreateSaleDto } from './dto/create-sale.dto';

@Controller('pos')
export class PosController {
  constructor(private readonly posService: PosService) {}

  @Post('sale')
  @HttpCode(HttpStatus.OK)
  async createSale(@Body() createSaleDto: CreateSaleDto) {
    return this.posService.processSale(createSaleDto);
  }

  @Get('products/search/:query')
  async searchProducts(@Param('query') query: string) {
    return this.posService.searchProducts(query);
  }

  @Post('receipt/print')
  async printReceipt(@Body('orderId') orderId: number) {
    return this.posService.printReceipt(orderId);
  }
}
```

#### 建立POS服務
```typescript
// src/pos/pos.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Product } from '../entities/product.entity';
import { Inventory } from '../entities/inventory.entity';
import { Order } from '../entities/order.entity';
import { OrderItem } from '../entities/order-item.entity';
import { CreateSaleDto } from './dto/create-sale.dto';

@Injectable()
export class PosService {
  private readonly logger = Logger;
  
  constructor(
    @InjectRepository(Product)
    private productRepository: Repository<Product>,
    @InjectRepository(Inventory)
    private inventoryRepository: Repository<Inventory>,
    @InjectRepository(Order)
    private orderRepository: Repository<Order>,
    @InjectRepository(OrderItem)
    private orderItemRepository: Repository<OrderItem>,
  ) {}

  async processSale(createSaleDto: CreateSaleDto) {
    // 1. 驗證商品存在且庫存充足
    const products = await this.validateProductsAndStock(createSaleDto.items);
    
    // 2. 建立訂單
    const order = await this.createOrder(createSaleDto, products);
    
    // 3. 扣減庫存
    await this.deductInventory(createSaleDto.items);
    
    // 4. 更新客戶積分
    if (createSaleDto.customerId) {
      await this.updateCustomerPoints(createSaleDto.customerId, order.totalAmount);
    }
    
    // 5. 生成小票
    const receipt = await this.generateReceipt(order);
    
    return { success: true, orderId: order.id, receipt };
  }

  private async validateProductsAndStock(items: any[]) {
    // 驗證邏輯實現
    return [];
  }

  private async createOrder(createSaleDto: CreateSaleDto, products: any[]) {
    // 訂單建立邏輯實現
    return {} as Order;
  }

  private async deductInventory(items: any[]) {
    // 庫存扣減邏輯實現
  }

  private async updateCustomerPoints(customerId: number, amount: number) {
    // 積分更新邏輯實現
  }

  private async generateReceipt(order: Order) {
    // 小票生成邏輯實現
    return {};
  }

  async searchProducts(query: string) {
    return this.productRepository.find({
      where: [
        { name: `%${query}%` },
        { author: `%${query}%` },
        { isbn: `%${query}%` }
      ],
      take: 20,
    });
  }
}
```

### 2. 庫存服務 (inventory-service)

#### 建立庫存控制器
```typescript
// src/inventory/inventory.controller.ts
import { Controller, Get, Post, Put, Delete, Body, Param, Query } from '@nestjs/common';
import { InventoryService } from './inventory.service';
import { CreateInventoryDto } from './dto/create-inventory.dto';
import { UpdateInventoryDto } from './dto/update-inventory.dto';

@Controller('inventory')
export class InventoryController {
  constructor(private readonly inventoryService: InventoryService) {}

  @Get()
  findAll(@Query() query: any) {
    return this.inventoryService.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.inventoryService.findOne(+id);
  }

  @Post()
  create(@Body() createInventoryDto: CreateInventoryDto) {
    return this.inventoryService.create(createInventoryDto);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateInventoryDto: UpdateInventoryDto) {
    return this.inventoryService.update(+id, updateInventoryDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.inventoryService.remove(+id);
  }

  @Post('adjust')
  adjustStock(@Body() body: any) {
    return this.inventoryService.adjustStock(body.productId, body.quantity, body.reason);
  }

  @Get('low-stock/alert')
  getLowStockAlert() {
    return this.inventoryService.getLowStockAlert();
  }
}
```

### 3. CRM服務 (crm-service)

#### 建立CRM控制器
```typescript
// src/crm/crm.controller.ts
import { Controller, Get, Post, Put, Body, Param, Query } from '@nestjs/common';
import { CrmService } from './crm.service';
import { CreateCustomerDto } from './dto/create-customer.dto';
import { UpdateCustomerDto } from './dto/update-customer.dto';

@Controller('crm')
export class CrmController {
  constructor(private readonly crmService: CrmService) {}

  @Get('customers')
  getAllCustomers(@Query() query: any) {
    return this.crmService.getAllCustomers(query);
  }

  @Get('customers/:id')
  getCustomer(@Param('id') id: string) {
    return this.crmService.getCustomer(+id);
  }

  @Post('customers')
  createCustomer(@Body() createCustomerDto: CreateCustomerDto) {
    return this.crmService.createCustomer(createCustomerDto);
  }

  @Put('customers/:id')
  updateCustomer(@Param('id') id: string, @Body() updateCustomerDto: UpdateCustomerDto) {
    return this.crmService.updateCustomer(+id, updateCustomerDto);
  }

  @Get('customers/:id/purchase-history')
  getPurchaseHistory(@Param('id') customerId: string) {
    return this.crmService.getPurchaseHistory(+customerId);
  }

  @Post('customers/:id/rewards')
  updateRewards(@Param('id') customerId: string, @Body() body: any) {
    return this.crmService.updateRewards(+customerId, body.points);
  }

  @Get('analytics/customer-behavior')
  getCustomerBehaviorAnalytics(@Query() query: any) {
    return this.crmService.getCustomerBehaviorAnalytics(query);
  }
}
```

### 4. API閘道 (api-gateway)

#### 使用Nginx作為API閘道
```nginx
# docker/nginx.conf
upstream pos_service {
    server pos-service:3000;
}

upstream inventory_service {
    server inventory-service:3000;
}

upstream crm_service {
    server crm-service:3000;
}

upstream report_service {
    server report-service:3000;
}

server {
    listen 80;
    
    # POS服務路由
    location /api/pos/ {
        proxy_pass http://pos_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 庫存服務路由
    location /api/inventory/ {
        proxy_pass http://inventory_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # CRM服務路由
    location /api/crm/ {
        proxy_pass http://crm_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 報表服務路由
    location /api/reports/ {
        proxy_pass http://report_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 靜態檔案服務
    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 前端應用開發

### 1. Web管理後台 (React + Ant Design)

#### 建立主應用組件
```typescript
// frontend/web-admin/src/App.tsx
import React from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { DashboardOutlined, ShoppingCartOutlined, UserOutlined, BarChartOutlined, DatabaseOutlined } from '@ant-design/icons';

import DashboardPage from './pages/Dashboard';
import PosPage from './pages/Pos';
import InventoryPage from './pages/Inventory';
import CrmPage from './pages/Crm';
import ReportsPage from './pages/Reports';

const { Header, Content, Footer, Sider } = Layout;

const App: React.FC = () => {
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="logo" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
        <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}>
          <Menu.Item key="/dashboard" icon={<BarChartOutlined />}>
            <Link to="/dashboard">儀表板</Link>
          </Menu.Item>
          <Menu.Item key="/pos" icon={<ShoppingCartOutlined />}>
            <Link to="/pos">POS系統</Link>
          </Menu.Item>
          <Menu.Item key="/inventory" icon={<DatabaseOutlined />}>
            <Link to="/inventory">庫存管理</Link>
          </Menu.Item>
          <Menu.Item key="/crm" icon={<UserOutlined />}>
            <Link to="/crm">客戶管理</Link>
          </Menu.Item>
          <Menu.Item key="/reports" icon={<BarChartOutlined />}>
            <Link to="/reports">報表分析</Link>
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: '#fff' }} />
        <Content style={{ margin: '24px 16px 0' }}>
          <Breadcrumb style={{ margin: '16px 0' }}>
            <Breadcrumb.Item>首頁</Breadcrumb.Item>
            <Breadcrumb.Item>{location.pathname.substring(1)}</Breadcrumb.Item>
          </Breadcrumb>
          <div style={{ padding: 24, background: '#fff', minHeight: 360 }}>
            <Routes>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/pos" element={<PosPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/crm" element={<CrmPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/" element={<DashboardPage />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>瓊林圖書事業有限公司 ©2026</Footer>
      </Layout>
    </Layout>
  );
};

export default App;
```

#### 建立儀表板組件
```typescript
// frontend/web-admin/src/pages/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Typography } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const { Title: AntTitle } = Typography;

const DashboardPage: React.FC = () => {
  const [salesData, setSalesData] = useState<any>(null);
  const [inventoryData, setInventoryData] = useState<any>(null);

  // 模擬API調用
  useEffect(() => {
    // 銷售趨勢數據
    setSalesData({
      labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
      datasets: [
        {
          label: '銷售額',
          data: [12000, 19000, 15000, 18000, 22000, 17000],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
        },
      ],
    });

    // 庫存數據
    setInventoryData({
      labels: ['正常', '低庫存', '缺貨'],
      datasets: [
        {
          data: [75, 15, 10],
          backgroundColor: [
            'rgba(75, 192, 192, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(255, 99, 132, 0.8)',
          ],
        },
      ],
    });
  }, []);

  const salesOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '銷售趨勢',
      },
    },
  };

  const inventoryOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '庫存狀態分布',
      },
    },
  };

  return (
    <div>
      <AntTitle level={2}>業務儀表板</AntTitle>
      
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日銷售額"
              value={12389}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              prefix={<ArrowUpOutlined />}
              suffix="NT$"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日訂單數"
              value={123}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="庫存商品數"
              value={1289}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="會員數"
              value={12893}
              precision={0}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={16}>
          <Card title="銷售趨勢">
            {salesData && <Line options={salesOptions} data={salesData} />}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="庫存狀態">
            {inventoryData && <Pie options={inventoryOptions} data={inventoryData} />}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="近期訂單">
            <Table 
              dataSource={[
                { id: 1, customer: '張三', amount: 1200, date: '2026-01-21', status: '已完成' },
                { id: 2, customer: '李四', amount: 850, date: '2026-01-21', status: '處理中' },
                { id: 3, customer: '王五', amount: 2100, date: '2026-01-20', status: '已完成' },
                { id: 4, customer: '趙六', amount: 550, date: '2026-01-20', status: '已取消' },
              ]}
              columns={[
                { title: '訂單編號', dataIndex: 'id', key: 'id' },
                { title: '客戶', dataIndex: 'customer', key: 'customer' },
                { title: '金額', dataIndex: 'amount', key: 'amount', render: (text) => `${text} NT$` },
                { title: '日期', dataIndex: 'date', key: 'date' },
                { title: '狀態', dataIndex: 'status', key: 'status' },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
```

### 2. POS前端 (Electron)

#### 建立POS主窗口
```typescript
// frontend/pos-app/src/main.ts
import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
    },
    resizable: true,
    icon: path.join(__dirname, '../assets/icon.png'),
    width: 1200,
  });

  // 加載應用
  if (app.isPackaged) {
    mainWindow.loadFile(path.join(__dirname, '../index.html'));
  } else {
    mainWindow.loadFile(path.join(process.env.PUBLIC_DIR!, 'index.html'));
  }

  // 打開開發者工具
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC處理
ipcMain.handle('print-receipt', async (event, orderId) => {
  // 列印小票邏輯
  return { success: true, message: '小票列印完成' };
});
```

## 資料庫設計實現

### 1. 建立資料庫模型
```typescript
// shared/models/entities/product.entity.ts
import { Entity, Column, PrimaryGeneratedColumn, ManyToOne, OneToMany, JoinColumn } from 'typeorm';
import { Category } from './category.entity';
import { OrderItem } from './order-item.entity';

@Entity('products')
export class Product {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 255 })
  name: string;

  @Column({ type: 'varchar', length: 255, nullable: true })
  author?: string;

  @Column({ type: 'varchar', length: 255, nullable: true })
  publisher?: string;

  @Column({ type: 'varchar', length: 13, unique: true, nullable: true })
  isbn?: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number;

  @Column({ type: 'int', default: 0 })
  cost: number;

  @Column({ type: 'int', default: 1 }) // 1: 上架, 0: 下架
  status: number;

  @Column({ type: 'text', nullable: true })
  description?: string;

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP', onUpdate: 'CURRENT_TIMESTAMP' })
  updatedAt: Date;

  @ManyToOne(() => Category, category => category.products)
  @JoinColumn({ name: 'category_id' })
  category: Category;

  @OneToMany(() => OrderItem, orderItem => orderItem.product)
  orderItems: OrderItem[];
}
```

### 2. 資料庫遷移腳本
```sql
-- migrations/001-initial-schema.sql
BEGIN;

-- 建立分類表
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立商品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    publisher VARCHAR(255),
    isbn VARCHAR(13) UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    cost INT DEFAULT 0,
    status INT DEFAULT 1,
    category_id INT REFERENCES categories(id),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立供應商表
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    payment_terms VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立庫存表
CREATE TABLE IF NOT EXISTS inventory (
    product_id INT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 0,
    safety_stock INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立客戶表
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    member_level VARCHAR(20) DEFAULT 'regular',
    points INT DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    registration_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立訂單表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    total_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    final_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    order_number VARCHAR(50) UNIQUE,
    payment_method VARCHAR(20),
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立訂單明細表
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立採購單表
CREATE TABLE IF NOT EXISTS purchase_orders (
    id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES suppliers(id),
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    expected_delivery_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立採購單明細表
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id SERIAL PRIMARY KEY,
    purchase_order_id INT REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL
);

-- 建立庫存變動記錄表
CREATE TABLE IF NOT EXISTS inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'in', 'out', 'adjustment'
    quantity_change INT NOT NULL,
    reason VARCHAR(100),
    reference_id INT, -- 訂單ID或採購單ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_isbn ON products(isbn);
CREATE INDEX idx_inventory_quantity ON inventory(quantity);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

COMMIT;
```

## 系統整合與同步

### 1. WebSocket即時通訊實現
```typescript
// backend/shared/websocket.gateway.ts
import { WebSocketGateway, WebSocketServer, SubscribeMessage, OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect } from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger } from '@nestjs/common';

@WebSocketGateway({
  cors: {
    origin: '*',
    credentials: true,
  },
})
export class WebSocketGateway implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server: Server;
  private logger: Logger = new Logger('WebSocketGateway');

  afterInit(server: Server) {
    this.logger.log('WebSocket Gateway 初始化完成');
  }

  handleConnection(client: Socket, ...args: any[]) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('inventory-update')
  handleInventoryUpdate(client: Socket, payload: any) {
    // 廣播庫存更新給所有連接的POS終端
    this.server.emit('inventory-updated', payload);
    return { success: true, message: '庫存更新已廣播' };
  }

  @SubscribeMessage('order-created')
  handleOrderCreated(client: Socket, payload: any) {
    // 廣播新訂單給相關模組
    this.server.emit('new-order', payload);
    return { success: true, message: '新訂單已廣播' };
  }

  // 發送庫存更新通知
  emitInventoryUpdate(productId: number, newQuantity: number) {
    this.server.emit('inventory-updated', {
      productId,
      newQuantity,
      timestamp: new Date(),
    });
  }

  // 發送訂單狀態更新
  emitOrderStatusUpdate(orderId: number, status: string) {
    this.server.emit('order-status-updated', {
      orderId,
      status,
      timestamp: new Date(),
    });
  }
}
```

### 2. 事件驅動架構實現
```typescript
// backend/shared/event-emitter.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';

@Injectable()
export class EventService {
  private readonly logger = new Logger(EventService.name);

  constructor(private eventEmitter: EventEmitter2) {}

  // 商品銷售事件
  emitProductSoldEvent(saleData: any) {
    this.eventEmitter.emit('product.sold', saleData);
    this.logger.log(`商品銷售事件觸發: ${JSON.stringify(saleData)}`);
  }

  // 訂單創建事件
  emitOrderCreatedEvent(orderData: any) {
    this.eventEmitter.emit('order.created', orderData);
    this.logger.log(`訂單創建事件觸發: ${JSON.stringify(orderData)}`);
  }

  // 庫存變更事件
  emitInventoryChangedEvent(inventoryData: any) {
    this.eventEmitter.emit('inventory.changed', inventoryData);
    this.logger.log(`庫存變更事件觸發: ${JSON.stringify(inventoryData)}`);
  }

  // 客戶積分變更事件
  emitCustomerPointsChangedEvent(pointsData: any) {
    this.eventEmitter.emit('customer.points.changed', pointsData);
    this.logger.log(`客戶積分變更事件觸發: ${JSON.stringify(pointsData)}`);
  }
}
```

## 測試策略

### 1. 單元測試
```typescript
// backend/pos-service/src/pos/pos.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { PosService } from './pos.service';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Product } from '../../entities/product.entity';
import { Inventory } from '../../entities/inventory.entity';
import { Order } from '../../entities/order.entity';
import { OrderItem } from '../../entities/order-item.entity';

describe('PosService', () => {
  let service: PosService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        PosService,
        {
          provide: getRepositoryToken(Product),
          useValue: {},
        },
        {
          provide: getRepositoryToken(Inventory),
          useValue: {},
        },
        {
          provide: getRepositoryToken(Order),
          useValue: {},
        },
        {
          provide: getRepositoryToken(OrderItem),
          useValue: {},
        },
      ],
    }).compile();

    service = module.get<PosService>(PosService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('processSale', () => {
    it('should process a sale successfully', async () => {
      // 測試邏輯
      expect(1).toBe(1);
    });
  });
});
```

### 2. 整合測試
```typescript
// tests/integration/pos-flow.test.ts
import * as request from 'supertest';
import { Test } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import { AppModule } from '../../backend/app.module';

describe('POS Flow Integration Tests', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('/api/pos/sale (POST) - should create a sale', async () => {
    const saleData = {
      items: [
        { productId: 1, quantity: 2, unitPrice: 100 },
      ],
      customerId: 1,
      paymentMethod: 'cash',
    };

    return request(app.getHttpServer())
      .post('/api/pos/sale')
      .send(saleData)
      .expect(200)
      .then(response => {
        expect(response.body.success).toBe(true);
        expect(response.body.orderId).toBeDefined();
      });
  });
});
```

## 部署配置

### 1. Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL資料庫
  postgres:
    image: postgres:14
    container_name: qionglin_inventory_postgres
    environment:
      POSTGRES_DB: qionglin_inventory_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    restart: unless-stopped

  # Redis快取
  redis:
    image: redis:7-alpine
    container_name: qionglin_inventory_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # POS服務
  pos-service:
    build:
      context: ./backend/pos-service
      dockerfile: Dockerfile
    container_name: qionglin_pos_service
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://admin:password123@postgres:5432/qionglin_inventory_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your_jwt_secret
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # 庫存服務
  inventory-service:
    build:
      context: ./backend/inventory-service
      dockerfile: Dockerfile
    container_name: qionglin_inventory_service
    ports:
      - "3002:3000"
    environment:
      - DATABASE_URL=postgresql://admin:password123@postgres:5432/qionglin_inventory_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your_jwt_secret
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # CRM服務
  crm-service:
    build:
      context: ./backend/crm-service
      dockerfile: Dockerfile
    container_name: qionglin_crm_service
    ports:
      - "3003:3000"
    environment:
      - DATABASE_URL=postgresql://admin:password123@postgres:5432/qionglin_inventory_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your_jwt_secret
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # API閘道
  api-gateway:
    image: nginx:alpine
    container_name: qionglin_api_gateway
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/web-admin/build:/usr/share/nginx/html
    depends_on:
      - pos-service
      - inventory-service
      - crm-service
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 2. GitHub Actions CI/CD
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    strategy:
      matrix:
        node-version: [18.x]

    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        
    - name: Install dependencies
      run: |
        cd backend/pos-service && npm ci
        cd ../inventory-service && npm ci
        cd ../crm-service && npm ci
        cd ../report-service && npm ci
        cd ../api-gateway && npm ci
        
    - name: Run linting
      run: |
        cd backend/pos-service && npm run lint
        cd ../inventory-service && npm run lint
        cd ../crm-service && npm run lint
        
    - name: Run tests
      run: |
        cd backend/pos-service && npm run test
        cd ../inventory-service && npm run test
        cd ../crm-service && npm run test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'
        
    - name: Build frontend
      run: |
        cd frontend/web-admin
        npm ci
        npm run build
        
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
        
    - name: Build and push Docker images
      run: |
        docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-pos:latest backend/pos-service
        docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-inventory:latest backend/inventory-service
        docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-crm:latest backend/crm-service
        docker push ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-pos:latest
        docker push ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-inventory:latest
        docker push ${{ secrets.DOCKERHUB_USERNAME }}/qionglin-crm:latest
        
    - name: Deploy to production
      run: |
        # 部署指令
        echo "Deploying to production..."
```

## 總結

本開發實施指南提供了瓊林圖書事業有限公司進銷存/客戶管理/POS系統整合專案的完整實施方案。通過模組化設計、微服務架構和現代化技術棧，確保系統的可擴展性、可靠性和易維護性。

開發團隊應按照此指南逐步實施，並在每個階段進行充分測試，以確保最終交付的系統符合業務需求和技術標準。