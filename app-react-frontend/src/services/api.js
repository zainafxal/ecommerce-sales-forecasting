const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const fetchJson = async (url, options = {}) => {
    const { timeoutMs = 8000, ...fetchOptions } = options;
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    try {
        const response = await fetch(url, {
            cache: 'no-store',
            ...fetchOptions,
            signal: controller.signal,
        });

        let data = null;
        try {
            data = await response.json();
        } catch (parseError) {
            data = null;
        }

        if (!response.ok) {
            const error = new Error(data?.detail || 'Request failed');
            error.status = response.status;
            throw error;
        }

        return data;
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timed out while waiting for the backend.');
        }
        throw error;
    } finally {
        window.clearTimeout(timeoutId);
    }
};

export const getApiHealth = async (options = {}) => {
    return await fetchJson(`${API_BASE_URL}/health`, {
        method: 'GET',
        timeoutMs: 6000,
        ...options,
    });
};

export const predictSales = async (data) => {
    try {
        return await fetchJson(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            timeoutMs: 20000,
        });
    } catch (error) {
        if (error.status === 429) {
            throw new Error(error.message || 'Rate limit exceeded. Please wait and try again.');
        }
        console.error('Error predicting sales:', error);
        throw error;
    }
};
