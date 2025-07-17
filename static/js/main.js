// ملف JavaScript الرئيسي

// رابط API الخاص بالموقع
const API_URL = 'https://erp-alraed.com/api';

// دالة لعرض رسائل النجاح
function showSuccess(message) {
    alert('✅ ' + message);
}

// دالة لعرض رسائل الخطأ
function showError(message) {
    alert('❌ ' + message);
}

// دالة لتحميل البيانات من الخادم
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error('حدث خطأ في جلب البيانات');
        }
        return await response.json();
    } catch (error) {
        showError(error.message);
        return null;
    }
}

// دالة لإرسال البيانات إلى الخادم
async function postData(endpoint, data) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('حدث خطأ في إرسال البيانات');
        }
        
        return await response.json();
    } catch (error) {
        showError(error.message);
        return null;
    }
}

// دالة لتنسيق التاريخ
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('ar-SA');
}

// دالة لتنسيق المبلغ
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(amount);
}
