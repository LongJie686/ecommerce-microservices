// API Gateway configuration for microservices architecture
// All API calls go through the gateway at port 8001
const API_BASE = window.location.origin;

// Login page goes directly to gateway
const API = {
    // User service
    LOGIN: `${API_BASE}/api/users/login`,
    REGISTER: `${API_BASE}/api/users/register`,
    PROFILE: (userId) => `${API_BASE}/api/users/${userId}`,

    // Product service
    PRODUCTS: `${API_BASE}/api/products`,
    HOT_PRODUCTS: `${API_BASE}/api/products/hot`,
    PRODUCT: (id) => `${API_BASE}/api/products/${id}`,
    CATEGORIES: `${API_BASE}/api/products/categories/all`,

    // Recommend service
    RECOMMEND: `${API_BASE}/api/recommend`,
    BEHAVIOR: `${API_BASE}/api/recommend/behavior`,

    // Crawler service
    CRAWLER_START: `${API_BASE}/api/crawler/start`,
    CRAWLER_TASKS: `${API_BASE}/api/crawler/tasks`,
    CRAWLER_RESULTS: (taskId) => `${API_BASE}/api/crawler/tasks/${taskId}/results`,

    // Analytics service
    DASHBOARD: `${API_BASE}/api/analytics/dashboard`,
    PRICE_DIST: `${API_BASE}/api/analytics/price-distribution`,
    SALES_TREND: `${API_BASE}/api/analytics/sales-trend`,
    SHOP_COMPARISON: `${API_BASE}/api/analytics/shop-comparison`,
};

// Auth token helper
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? {'Authorization': `Bearer ${token}`} : {};
}

// Authenticated fetch wrapper
async function apiFetch(url, options = {}) {
    const headers = {...getAuthHeaders(), ...options.headers};
    const resp = await fetch(url, {...options, headers});
    if (resp.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login.html';
        return;
    }
    return resp.json();
}
