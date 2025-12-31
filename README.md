# SpatialDB Project

This project is a comprehensive spatial database solution designed to simplify the process of data collection, comparison, and mapping during market research and analysis. It integrates various geospatial tools into a unified Docker-based workflow.

## System Architecture

The system is built on a microservices architecture orchestrated by Docker Compose:

*   **Database**: PostGIS (Spatial Data Storage)
*   **Backend**: Flask (API & Geocoding Service)
*   **Geospatial Server**: GeoServer (WMS/WFS Services)
*   **Frontend**: MapStore (Web GIS Client) & PgAdmin (Database Management)

## Setup Instructions

This system uses [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to build and run all services. This ensures easy deployment and migration to any local or cloud environment.

### Services Overview

The `docker-compose.yml` orchestrates the following services:

- **`postgres`**: PostGIS database service for storing spatial data.
    - **Image:** `postgis/postgis:15-3.3`
    - **Port:** `5432`
- **`pgadmin`**: Web interface for managing the PostgreSQL database.
    - **Port:** `5050`
- **`geocoder_worker`**: Background service that converts addresses to coordinates using the Amap API.
- **`geoserver`**: Open-source server for sharing geospatial data.
    - **Image:** `kartoza/geoserver:2.27.1`
    - **Port:** `8080`
- **`geoserver_setup`**: One-time script to configure GeoServer on startup.
- **`mapstore`**: Web GIS client for creating, saving, and sharing maps.
    - **Image:** `geosolutionsit/mapstore2:latest`
    - **Port:** `3050`
- **`geoserver_auto_publish`**: Tool to automatically publish new PostGIS layers to GeoServer.

## Installation

1.  **Install Docker**: Ensure Docker and Docker Compose are installed on your system.

2.  **Clone Repository**: Clone this repository and navigate to the project root.

3.  **Configure API Keys**: Create a `.env` file or update `docker-compose.yml` with your Amap API Key.

    *   **Amap API Key**:
        Get a key from: [https://lbs.amap.com/api/webservice/guide/api/georegeo](https://lbs.amap.com/api/webservice/guide/api/georegeo)

    ```yaml
    geocoder_worker:
      environment:
        AMAP_KEY: YOUR_API_KEY_HERE
    ```

4.  **Initial Data (Optional)**: Edit `init-scripts/init.sql` and `init-scripts/comparable_products.csv` to customize initial data.

5.  **Run**: Build and start the containers.

    ```bash
    docker-compose up --build
    ```

## Usage

Once the services are running, access them via your browser:

### 1. PgAdmin - Database Management
*   **URL:** `http://localhost:5050`
*   **Email:** `admin@company.com`
*   **Password:** `admin`

*   Right-click a table -> "View/Edit Data" -> "All Rows".
*   **Note**: When adding a new entry with an address, the geocoding service runs automatically within 10 seconds.

### 2. MapStore - Map Creation
*   **URL:** `http://localhost:3050/mapstore/`
*   **Username:** `admin`
*   **Password:** `admin`

**Steps to Add a Layer:**
1.  Create a new map.
2.  Click `+` to add a catalog service.
3.  Select **WFS** service type.
4.  Service URL: `http://geoserver:8080/geoserver/wfs`
5.  Search and add your layer to the map.

## Common Commands

*   **Start Services:**
    ```bash
    docker-compose up --build
    ```

*   **Stop & Clean:**
    ```bash
    docker-compose down --volumes --remove-orphans
    ```

### Example SQL Queries

*   **Find all projects within 5000m of project id=1:**
    ```sql
    SELECT *
    FROM project_data
    WHERE ST_DWithin(
        geom_wgs84::geography,
        (SELECT geom_wgs84 FROM project_data WHERE id = 1)::geography,
        5000
    );
    ```

*   **Calculate distance to target (id=99) and update:**
    ```sql
    UPDATE project_data
    SET distance_to_target_km = ST_Distance(
        geom_wgs84::geography,
        (SELECT geom_wgs84 FROM project_data WHERE id = 99)::geography
    ) / 1000;
    ```

## Future Work

*   **Public Transit Integration**: Upload transit data to enable complex spatial queries (e.g., find apartments within 500m of a subway station with rent < X).

*   **Efficiency Analysis**: Create charts to analyze the correlation between distance to transit and cost efficiency.

*   **Travel Time**: Extend `geocoder_worker` to calculate walking/biking time to the nearest station using the Amap API.

## Technical Highlights & Compliance

This project demonstrates rigorous handling of complex geospatial data standards:

*   **Dual Coordinate System Support**: The system automatically manages both global **WGS-84** (EPSG:4326) and the national standard **GCJ-02** (EPSG:4490) coordinate systems.
*   **Automated Transformation**: The geocoding worker integrates a robust conversion algorithm to transform Amap API results (GCJ-02) into WGS-84 for global analysis compatibility while preserving the original national standard coordinates for local compliance and accuracy.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See the `LICENSE` file for details.

---

# 空间数据库项目 (中文文档)

本项目是一个综合的空间数据库解决方案，旨在简化市场研究和分析过程中的数据收集、比较和地图绘制流程。它将各种地理空间工具集成到一个统一的基于 Docker 的工作流程中。

## 系统架构

该系统基于微服务架构，由 Docker Compose 编排：

*   **数据库**: PostGIS (空间数据存储)
*   **后端**: Flask (API 及地理编码服务)
*   **地理空间服务器**: GeoServer (WMS/WFS 服务)
*   **前端**: MapStore (Web GIS 客户端) & PgAdmin (数据库管理)

## 设置说明

该系统使用 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/) 来构建和运行所有服务。这确保了可以轻松部署和迁移到任何本地或云环境。

### 服务概览

`docker-compose.yml` 文件编排了以下服务：

- **`postgres`**: 用于存储空间数据的 PostGIS 数据库服务。
    - **镜像:** `postgis/postgis:15-3.3`
    - **端口:** `5432`
- **`pgadmin`**: 用于管理 PostgreSQL 数据库的网页界面。
    - **端口:** `5050`
- **`geocoder_worker`**: 后台服务，使用高德地图 API 将地址转换为地理坐标。
- **`geoserver`**: 用于托管地理空间数据的开源服务器。
    - **镜像:** `kartoza/geoserver:2.27.1`
    - **端口:** `8080`
- **`geoserver_setup`**: 用于在启动时自动配置 GeoServer 的一次性脚本。
- **`mapstore`**: 用于创建、保存和共享地图的 Web GIS 客户端。
    - **镜像:** `geosolutionsit/mapstore2:latest`
    - **端口:** `3050`
- **`geoserver_auto_publish`**: 自动将新的 PostGIS 图层发布到 GeoServer 的工具服务。

## 安装

1.  **安装 Docker**：确保您的系统上已安装 Docker 和 Docker Compose。

2.  **克隆仓库**：克隆此代码库并导航到项目根目录。

3.  **配置 API 密钥**：创建 `.env` 文件或更新 `docker-compose.yml` 中的高德地图 API 密钥。

    *   **高德地图 API Key**:
        申请密钥：[https://lbs.amap.com/api/webservice/guide/api/georegeo](https://lbs.amap.com/api/webservice/guide/api/georegeo)

    ```yaml
    geocoder_worker:
      environment:
        AMAP_KEY: YOUR_API_KEY_HERE
    ```

4.  **初始数据（可选）**：编辑 `init-scripts/init.sql` 和 `init-scripts/comparable_products.csv` 以自定义初始数据。

5.  **运行**：构建并启动容器。

    ```bash
    docker-compose up --build
    ```

## 使用方法

服务运行后，通过浏览器访问：

### 1. PgAdmin - 数据库管理
*   **地址:** `http://localhost:5050`
*   **邮箱:** `admin@company.com`
*   **密码:** `admin`

*   右键单击表 -> “查看/编辑数据” -> “所有行”。
*   **注意**：当添加带有地址的新条目时，地理编码服务将在 10 秒内在后台自动运行。

### 2. MapStore - 地图制作
*   **地址:** `http://localhost:3050/mapstore/`
*   **用户名:** `admin`
*   **密码:** `admin`

**添加图层步骤:**
1.  创建一个新地图。
2.  点击 `+` 号添加目录服务。
3.  选择 **WFS** 服务类型。
4.  服务地址: `http://geoserver:8080/geoserver/wfs`
5.  搜索并将图层添加到地图。

## 常用命令

*   **启动服务:**
    ```bash
    docker-compose up --build
    ```

*   **停止并清理:**
    ```bash
    docker-compose down --volumes --remove-orphans
    ```

### SQL 查询示例

*   **选择 id=1 项目附近 5000m 的所有项目：**
    ```sql
    SELECT *
    FROM project_data
    WHERE ST_DWithin(
        geom_wgs84::geography,
        (SELECT geom_wgs84 FROM project_data WHERE id = 1)::geography,
        5000
    );
    ```

*   **计算所有项目到项目 id=99 的直线距离并更新字段：**
    ```sql
    UPDATE project_data
    SET distance_to_target_km = ST_Distance(
        geom_wgs84::geography,
        (SELECT geom_wgs84 FROM project_data WHERE id = 99)::geography
    ) / 1000;
    ```

## 未来展望

*   **公共交通集成**：上传公交或地铁数据，进行复杂的空间查询（如：查找距离地铁站 500m 内且租金低于 X 的房源）。

*   **坪效分析**：创建图表分析距离与坪效（sqm efficiency）的相关性。

*   **出行时间计算**：扩展 `geocoder_worker`，利用高德 API 计算步行或骑行到最近地铁站的时间。



## 技术亮点与合规性 (Technical Highlights)



本项目展示了对复杂地理空间数据标准的严谨处理能力：



*   **双坐标系支持**：系统自动管理全球通用的 **WGS-84** (EPSG:4326) 和国家标准 **GCJ-02** (EPSG:4490) 两种坐标系。

*   **自动转换与合规**：地理编码服务集成了转换算法，将高德地图 API 返回的火星坐标 (GCJ-02) 转换为 WGS-84 以进行通用空间分析，同时保留原始国家标准坐标，确保数据在本地应用中的精确性与合规性。



## 许可证 (License)



本项目采用 GNU Affero General Public License v3.0 (AGPLv3) 许可证。详情请参阅 `LICENSE` 文件。
