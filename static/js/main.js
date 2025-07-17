// API Base URL
const API_BASE_URL = '/api';

// Utility Functions
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(amount);
};

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-SA');
};

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// API Functions
const API = {
    // Get all suppliers
    async getSuppliers() {
        try {
            const response = await fetch(`${API_BASE_URL}/suppliers`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching suppliers:', error);
            return [];
        }
    },
    
    // Get all invoices
    async getInvoices() {
        try {
            const response = await fetch(`${API_BASE_URL}/invoices`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching invoices:', error);
            return [];
        }
    },
    
    // Add new invoice
    async addInvoice(invoiceData) {
        try {
            const response = await fetch(`${API_BASE_URL}/invoices`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(invoiceData)
            });
            
            if (!response.ok) throw new Error('Failed to add invoice');
            
            return await response.json();
        } catch (error) {
            console.error('Error adding invoice:', error);
            throw error;
        }
    },
    
    // Get purchase orders
    async getPurchaseOrders() {
        try {
            const response = await fetch(`${API_BASE_URL}/purchase-orders`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching purchase orders:', error);
            return [];
        }
    },
    
    // Add purchase order
    async addPurchaseOrder(orderData) {
        try {
            const response = await fetch(`${API_BASE_URL}/purchase-orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            });
            
            if (!response.ok) throw new Error('Failed to add purchase order');
            
            return await response.json();
        } catch (error) {
            console.error('Error adding purchase order:', error);
            throw error;
        }
    },
    
    // Get payments
    async getPayments(supplierId = null) {
        try {
            const url = supplierId 
                ? `${API_BASE_URL}/payments?supplier_id=${supplierId}`
                : `${API_BASE_URL}/payments`;
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error fetching payments:', error);
            return [];
        }
    },
    
    // Add payment
    async addPayment(paymentData) {
        try {
            const response = await fetch(`${API_BASE_URL}/payments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(paymentData)
            });
            
            if (!response.ok) throw new Error('Failed to add payment');
            
            return await response.json();
        } catch (error) {
            console.error('Error adding payment:', error);
            throw error;
        }
    }
};

// Add CSS animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
window.API = API;
window.showNotification = showNotification;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
