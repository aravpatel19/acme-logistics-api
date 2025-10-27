// Dashboard configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'acme_dev_test_key_123';
const REFRESH_INTERVAL = 15000; // 15 seconds - less glitchy

// State management
let allLoads = [];
let filteredLoads = [];
let selectedLoad = null;
let currentTab = 'available';
let currentView = 'loads';
let equipmentFilter = '';
let searchQuery = '';
let metrics = null;
let lastUpdateTime = 0;

// Chart instances
let outcomesChart = null;
let sentimentChart = null;

// Initialize dashboard
async function init() {
    console.log('Initializing dashboard...');
    
    // Initial load
    await updateDashboard();
    
    // Set up event listeners
    const searchInput = document.getElementById('loadSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            filterLoads();
        });
    }
    
    // Set up auto-refresh with throttling
    setInterval(() => {
        const now = Date.now();
        if (now - lastUpdateTime > REFRESH_INTERVAL - 1000) {
            updateDashboard();
        }
    }, REFRESH_INTERVAL);
}

// Switch between main views
function switchView(view) {
    currentView = view;
    
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('nav-active');
        if (btn.dataset.view === view) {
            btn.classList.add('nav-active');
        }
    });
    
    // Show/hide views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.add('hidden');
    });
    
    const viewElement = document.getElementById(`${view}View`);
    if (viewElement) {
        viewElement.classList.remove('hidden');
        viewElement.classList.add('flex');
    }
    
    // Update data for the view
    if (view === 'calls') {
        updateCallsTable();
    } else if (view === 'analytics') {
        updateAnalytics();
    }
}

// Switch tabs in loads view
function switchTab(tab) {
    currentTab = tab;
    
    // Update tab UI
    const tabs = document.querySelectorAll('.flex.space-x-6 button');
    tabs.forEach(t => {
        t.classList.remove('tab-active', 'text-gray-400');
        if (t.textContent.toLowerCase().includes(tab)) {
            t.classList.add('tab-active');
        } else {
            t.classList.add('text-gray-400');
        }
    });
    
    filterLoads();
}

// Filter by equipment type
function filterByEquipment(type) {
    equipmentFilter = type;
    
    // Update button states
    const buttons = document.querySelectorAll('.flex.gap-2 button');
    buttons.forEach(btn => {
        if ((type === '' && btn.textContent.includes('All')) || 
            (type !== '' && btn.textContent.trim() === type)) {
            btn.classList.add('bg-blue-600');
            btn.classList.remove('bg-gray-700');
        } else {
            btn.classList.remove('bg-blue-600');
            btn.classList.add('bg-gray-700');
        }
    });
    
    filterLoads();
}

// Filter loads based on current filters
function filterLoads() {
    filteredLoads = allLoads.filter(load => {
        // Tab filter
        if (currentTab === 'available' && load.status !== 'Available') return false;
        if (currentTab === 'booked' && load.status !== 'Booked') return false;
        // 'all' tab shows everything
        
        // Equipment filter
        if (equipmentFilter && load.equipment_type !== equipmentFilter) return false;
        
        // Search filter
        if (searchQuery) {
            const searchableText = `${load.load_id} ${load.origin} ${load.destination} ${load.equipment_type}`.toLowerCase();
            if (!searchableText.includes(searchQuery)) return false;
        }
        
        return true;
    });
    
    updateLoadsList();
}

// Fetch data from API
async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching metrics:', error);
        return null;
    }
}

async function fetchLoads() {
    try {
        // Fetch ALL loads including booked ones for dashboard
        const response = await fetch(`${API_BASE_URL}/api/v1/loads?include_booked=true&t=${Date.now()}`, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const loads = data.body && data.body.loads ? data.body.loads : [];
        
        console.log(`Fetched ${loads.length} loads from database`);
        return loads;
    } catch (error) {
        console.error('Error fetching loads:', error);
        return [];
    }
}

// Update dashboard data
async function updateDashboard() {
    lastUpdateTime = Date.now();
    console.log('Updating dashboard...');
    
    try {
        const [newMetrics, loads] = await Promise.all([
            fetchMetrics(),
            fetchLoads()
        ]);
        
        if (newMetrics) {
            metrics = newMetrics;
        }
        
        if (loads && loads.length > 0) {
            // Debug logging
            console.log(`Received ${loads.length} loads from API`);
            const bookedCount = loads.filter(l => l.status === 'booked').length;
            console.log(`Booked loads in response: ${bookedCount}`);
            
            // Use status directly from API response
            allLoads = loads.map(load => {
                return {
                    ...load,
                    status: load.status === 'booked' ? 'Booked' : 'Available'
                };
            });
            
            console.log(`After mapping - Booked: ${allLoads.filter(l => l.status === 'Booked').length}`);
            
            filterLoads();
            
            // Update count
            const countElement = document.getElementById('loadCount');
            if (countElement) {
                countElement.textContent = `${allLoads.length} total`;
            }
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Update loads list with minimal DOM manipulation
function updateLoadsList() {
    const container = document.getElementById('loadsList');
    if (!container) return;
    
    if (filteredLoads.length === 0) {
        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-inbox text-4xl mb-2"></i>
                <p>No loads found</p>
            </div>
        `;
        return;
    }
    
    const html = filteredLoads.map(load => {
        const pickupDate = new Date(load.pickup_datetime);
        const deliveryDate = new Date(load.delivery_datetime);
        const origin = load.origin.split(',')[0];
        const destination = load.destination.split(',')[0];
        const isSelected = selectedLoad && selectedLoad.load_id === load.load_id;
        
        const statusColors = {
            'Available': 'bg-green-600',
            'Booked': 'bg-blue-600',
            'Covered': 'bg-gray-600'
        };
        
        return `
            <div class="load-card bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600 ${isSelected ? 'selected' : ''}"
                 onclick="selectLoad('${load.load_id}')">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="font-bold text-lg">${load.load_id}</h3>
                    <span class="px-2 py-1 rounded text-xs ${statusColors[load.status] || 'bg-gray-600'}">
                        ${load.status}
                    </span>
                </div>
                
                <div class="space-y-2 text-sm">
                    <div class="flex items-center">
                        <div class="flex-1">
                            <p class="text-gray-400">${origin}</p>
                            <p class="text-xs text-gray-500">${pickupDate.toLocaleDateString()}</p>
                        </div>
                        <i class="fas fa-arrow-right mx-2 text-gray-500"></i>
                        <div class="flex-1 text-right">
                            <p class="text-gray-400">${destination}</p>
                            <p class="text-xs text-gray-500">${deliveryDate.toLocaleDateString()}</p>
                        </div>
                    </div>
                    
                    <div class="flex justify-between text-xs text-gray-500">
                        <span>${load.miles} miles</span>
                        <span>$${(load.posted_carrier_rate || load.loadboard_rate || 0).toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// Select a load
function selectLoad(loadId) {
    selectedLoad = allLoads.find(l => l.load_id === loadId);
    updateLoadsList();
    updateLoadDetails();
}

// Update load details panel
function updateLoadDetails() {
    const panel = document.getElementById('loadDetailsPanel');
    if (!panel) return;
    
    if (!selectedLoad) {
        panel.innerHTML = `
            <div class="h-full flex items-center justify-center text-gray-500">
                <div class="text-center">
                    <i class="fas fa-boxes text-6xl mb-4 opacity-20"></i>
                    <p class="text-lg">Select a load to view details</p>
                </div>
            </div>
        `;
        return;
    }
    
    const pickupDate = new Date(selectedLoad.pickup_datetime);
    const deliveryDate = new Date(selectedLoad.delivery_datetime);
    const rate = selectedLoad.posted_carrier_rate || selectedLoad.loadboard_rate || 0;
    const ratePerMile = selectedLoad.rate_per_mile || (rate / selectedLoad.miles);
    
    panel.innerHTML = `
        <div class="max-w-4xl mx-auto">
            <!-- Load Header -->
            <div class="flex justify-between items-start mb-6">
                <div>
                    <h2 class="text-3xl font-bold flex items-center">
                        Load ${selectedLoad.load_id}
                        <span class="ml-3 px-3 py-1 rounded text-sm ${
                            selectedLoad.status === 'Available' ? 'bg-green-600' : 
                            selectedLoad.status === 'Booked' ? 'bg-blue-600' : 'bg-gray-600'
                        }">
                            ${selectedLoad.status}
                        </span>
                    </h2>
                </div>
            </div>
            
            <!-- Route Information -->
            <div class="bg-gray-800 rounded-lg p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Route Information</h3>
                <div class="grid grid-cols-2 gap-6">
                    <div>
                        <p class="text-gray-400 text-sm mb-1">Origin</p>
                        <p class="font-medium flex items-center">
                            <i class="fas fa-map-marker-alt mr-2 text-green-500"></i>
                            ${selectedLoad.origin}
                        </p>
                        <p class="text-sm text-gray-500 mt-1">
                            ${pickupDate.toLocaleDateString()} at ${pickupDate.toLocaleTimeString('en-US', { 
                                hour: 'numeric', minute: '2-digit', hour12: true 
                            })}
                        </p>
                    </div>
                    <div>
                        <p class="text-gray-400 text-sm mb-1">Destination</p>
                        <p class="font-medium flex items-center">
                            <i class="fas fa-flag-checkered mr-2 text-red-500"></i>
                            ${selectedLoad.destination}
                        </p>
                        <p class="text-sm text-gray-500 mt-1">
                            ${deliveryDate.toLocaleDateString()} at ${deliveryDate.toLocaleTimeString('en-US', { 
                                hour: 'numeric', minute: '2-digit', hour12: true 
                            })}
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Load Details -->
            <div class="grid grid-cols-4 gap-4 mb-6">
                <div class="bg-gray-800 rounded-lg p-4">
                    <p class="text-gray-400 text-sm mb-1">Equipment</p>
                    <p class="font-medium flex items-center">
                        <i class="fas fa-truck mr-2"></i>
                        ${selectedLoad.equipment_type}
                    </p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <p class="text-gray-400 text-sm mb-1">Commodity</p>
                    <p class="font-medium">${selectedLoad.commodity_type || 'General'}</p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <p class="text-gray-400 text-sm mb-1">Weight</p>
                    <p class="font-medium">${selectedLoad.weight.toLocaleString()} lbs</p>
                </div>
                <div class="bg-gray-800 rounded-lg p-4">
                    <p class="text-gray-400 text-sm mb-1">Reference ID</p>
                    <p class="font-medium">${selectedLoad.load_id}</p>
                </div>
            </div>
            
            <!-- Pricing Information -->
            <div class="bg-gray-800 rounded-lg p-6 mb-6">
                <h3 class="text-lg font-semibold mb-4">Pricing</h3>
                <div class="grid grid-cols-3 gap-4">
                    <div>
                        <p class="text-gray-400 text-sm mb-1">Loadboard Rate</p>
                        <p class="text-2xl font-bold">$${rate.toLocaleString()}</p>
                    </div>
                    <div>
                        <p class="text-gray-400 text-sm mb-1">Rate per Mile</p>
                        <p class="text-2xl font-bold">$${ratePerMile.toFixed(2)}</p>
                    </div>
                    <div>
                        <p class="text-gray-400 text-sm mb-1">Max Buy (5% over)</p>
                        <p class="text-2xl font-bold text-yellow-500">$${selectedLoad.max_buy.toLocaleString()}</p>
                    </div>
                </div>
            </div>
            
            <!-- Notes Section -->
            ${selectedLoad.notes ? `
                <div class="bg-gray-800 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4">Notes</h3>
                    <p class="text-gray-300">${selectedLoad.notes}</p>
                </div>
            ` : ''}
        </div>
    `;
}

// Update calls table
function updateCallsTable() {
    const tbody = document.getElementById('callsTableBody');
    if (!tbody || !metrics || !metrics.recent_calls) {
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        No calls recorded yet
                    </td>
                </tr>
            `;
        }
        return;
    }
    
    const calls = metrics.recent_calls;
    
    tbody.innerHTML = calls.map(call => {
        const timestamp = new Date(call.timestamp);
        const load = allLoads.find(l => l.load_id === call.load_id);
        const route = load ? `${load.origin.split(',')[0]} → ${load.destination.split(',')[0]}` : '-';
        
        const outcomeColors = {
            'booked': 'bg-green-600',
            'no_agreement': 'bg-yellow-600',
            'not_interested': 'bg-red-600',
            'carrier_not_eligible': 'bg-gray-600'
        };
        
        const sentimentColors = {
            'positive': 'bg-green-600',
            'neutral': 'bg-yellow-600',
            'negative': 'bg-red-600'
        };
        
        return `
            <tr class="hover:bg-gray-700 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    ${timestamp.toLocaleString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm">${call.carrier_name || 'Unknown'}</div>
                    <div class="text-xs text-gray-500">MC ${call.mc_number}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    ${call.load_id || '-'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    ${route}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${outcomeColors[call.outcome] || 'bg-gray-600'}">
                        ${call.outcome.replace('_', ' ')}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${call.agreed_rate ? 'text-green-400' : ''}">
                    ${call.agreed_rate ? `$${call.agreed_rate.toLocaleString()}` : '-'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${sentimentColors[call.sentiment] || 'bg-gray-600'}">
                        ${call.sentiment}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

// Update analytics
function updateAnalytics() {
    if (!metrics) return;
    
    // Update KPIs
    document.getElementById('totalCalls').textContent = metrics.total_calls || 0;
    document.getElementById('successRate').textContent = `${metrics.success_rate || 0}%`;
    document.getElementById('totalBookedValue').textContent = `$${(metrics.total_booked_value || 0).toLocaleString()}`;
    document.getElementById('avgNegotiation').textContent = `${metrics.avg_negotiation_rounds || 0} rounds`;
    
    // Update charts
    if (metrics.calls_by_outcome) updateOutcomesChart(metrics.calls_by_outcome);
    if (metrics.sentiment_breakdown) updateSentimentChart(metrics.sentiment_breakdown);
}

// Update outcomes chart
function updateOutcomesChart(outcomes) {
    const ctx = document.getElementById('outcomesChart');
    if (!ctx) return;
    
    const data = {
        labels: Object.keys(outcomes).map(key => 
            key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
        ),
        datasets: [{
            data: Object.values(outcomes),
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444', '#6B7280', '#3B82F6', '#8B5CF6'],
            borderWidth: 0
        }]
    };
    
    if (outcomesChart) outcomesChart.destroy();
    
    outcomesChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9CA3AF' }
                }
            }
        }
    });
}

// Update sentiment chart
function updateSentimentChart(sentiments) {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;
    
    const data = {
        labels: Object.keys(sentiments).map(key => key.charAt(0).toUpperCase() + key.slice(1)),
        datasets: [{
            label: 'Calls',
            data: Object.values(sentiments),
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
            borderWidth: 0
        }]
    };
    
    if (sentimentChart) sentimentChart.destroy();
    
    sentimentChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, color: '#9CA3AF' },
                    grid: { color: '#374151' }
                },
                x: {
                    ticks: { color: '#9CA3AF' },
                    grid: { color: '#374151' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}