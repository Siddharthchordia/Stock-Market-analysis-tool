class PriceVolumeChart {
    constructor(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        this.ctx = canvas.getContext('2d');
        this.data = data;
        this.chart = null;

        this.init();
    }
    
    init() {
        this.renderRangeButtons();
        this.updateChartData(this.getDefaultRange());
    }

    renderRangeButtons() {
        const dates = this.data.dates;
        if (!dates || dates.length === 0) return;

        const firstDate = new Date(dates[0]);
        const lastDate = new Date(dates[dates.length - 1]);
        const diffDays = Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24));
        const diffMonths = diffDays / 30;
        const diffYears = diffDays / 365;

        this.ranges = [
            { label: '1M', valid: diffMonths >= 1 },
            { label: '6M', valid: diffMonths >= 6 },
            { label: '1Y', valid: diffYears >= 1 },
            { label: '3Y', valid: diffYears >= 3 },
            { label: '5Y', valid: diffYears >= 5 },
            { label: '10Y', valid: diffYears >= 10 },
            { label: 'MAX', valid: true }
        ];

        const container = document.getElementById('chart-range-controls');
        if (!container) return;
        container.innerHTML = '';

        this.ranges.forEach(range => {
            if (!range.valid) return;

            const btn = document.createElement('button');
            btn.textContent = range.label;
            btn.dataset.range = range.label;
            btn.className =
                'px-3 py-1 text-xs font-medium rounded-full transition-all ' +
                'text-slate-600 hover:bg-amber-100/60';

            btn.addEventListener('click', () => {
                this.setActiveRange(range.label);
            });

            container.appendChild(btn);
        });
    }

    getDefaultRange() {
        const valid = this.ranges.filter(r => r.valid && r.label !== 'MAX');
        return valid.length ? valid[valid.length - 1].label : 'MAX';
    }

    setActiveRange(label) {
        const container = document.getElementById('chart-range-controls');
        Array.from(container.children).forEach(btn => {
            if (btn.dataset.range === label) {
                btn.classList.add(
                    'bg-amber-400/90',
                    'text-white',
                    'shadow-md'
                );
                btn.classList.remove('text-slate-600');
            } else {
                btn.classList.remove(
                    'bg-amber-400/90',
                    'text-white',
                    'shadow-md'
                );
                btn.classList.add('text-slate-600');
            }
        });

        this.updateChartData(label);
    }

    getSlicedData(range) {
        if (range === 'MAX') return this.data;

        const lastDate = new Date(this.data.dates[this.data.dates.length - 1]);
        const startDate = new Date(lastDate);

        const map = {
            '1M': () => startDate.setMonth(startDate.getMonth() - 1),
            '6M': () => startDate.setMonth(startDate.getMonth() - 6),
            '1Y': () => startDate.setFullYear(startDate.getFullYear() - 1),
            '3Y': () => startDate.setFullYear(startDate.getFullYear() - 3),
            '5Y': () => startDate.setFullYear(startDate.getFullYear() - 5),
            '10Y': () => startDate.setFullYear(startDate.getFullYear() - 10)
        };

        map[range]?.();

        const startIndex = this.data.dates.findIndex(
            d => new Date(d) >= startDate
        );

        return {
            dates: this.data.dates.slice(startIndex),
            prices: this.data.prices.slice(startIndex),
            volumes: this.data.volumes.slice(startIndex),
            index_prices: this.data.index_prices ? this.data.index_prices.slice(startIndex) : []
        };
    }

    updateChartData(range) {
        const sliced = this.getSlicedData(range);

        if (this.chart) {
            this.chart.data.labels = sliced.dates;
            this.chart.data.datasets[0].data = sliced.volumes;
            this.chart.data.datasets[1].data = sliced.prices;
            if (this.chart.data.datasets[2]) {
                this.chart.data.datasets[2].data = sliced.index_prices;
            }
            this.chart.update();
        } else {
            this.renderChart(sliced);
        }
    }

    renderChart(data) {
        if (this.chart) this.chart.destroy();

        const datasets = [
            {
                label: 'Volume',
                type: 'bar',
                data: data.volumes,
                yAxisID: 'y-volume',
                backgroundColor: 'rgba(148, 163, 184, 0.35)', // slate glass
                barPercentage: 0.6,
                order: 3
            },
            {
                label: 'Price',
                type: 'line',
                data: data.prices,
                yAxisID: 'y-price',
                borderColor: '#F59E0B', // warm amber
                backgroundColor: 'rgba(251, 191, 36, 0.25)',
                borderWidth: 2.5,
                tension: 0.05,
                pointRadius: 0,
                fill: true,
                order: 1
            }
        ];

        // Add Nifty 50 dataset if available
        if (data.index_prices && data.index_prices.length > 0) {
            datasets.push({
                label: 'Nifty 50',
                type: 'line',
                data: data.index_prices,
                yAxisID: 'y-index',
                borderColor: '#0F766E',
                borderWidth: 2,
                tension: 0.05,
                pointRadius: 0,
                fill: false,
                spanGaps: true,
                order: 2
            });
        }

        this.chart = new Chart(this.ctx, {
            data: {
                labels: data.dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        borderColor: 'rgba(0,0,0,0.08)',
                        borderWidth: 1,
                        titleColor: '#0F172A',
                        bodyColor: '#0F172A',
                        callbacks: {
                            label: ctx => {
                                const v = ctx.parsed.y;
                                if (v === null || v === undefined) return null;

                                if (ctx.dataset.yAxisID === 'y-price') {
                                    return `Price: ₹${v.toLocaleString('en-IN')}`;
                                }
                                if (ctx.dataset.yAxisID === 'y-index') {
                                    return `Nifty 50: ${v.toLocaleString('en-IN')}`;
                                }
                                return `Volume: ${v.toLocaleString('en-IN')}`;
                            }
                        }
                    }
                },
                
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#64748B',
                            maxTicksLimit: isMobile ? 2:8,
                            display : true
                        }
                    },
                    'y-volume': {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true,
                        grid: { display: false },
                        ticks: { display: false } // Hide volume ticks to save space
                    },
                    'y-price': {
                        type: 'linear',
                        position: 'right',
                        grid: {
                            color: 'rgba(15,23,42,0.04)',
                            borderDash: [3, 6]
                        },
                        ticks: { color: '#64748B' }
                    },
                    'y-index': {
                        type: 'linear',
                        position: 'right',
                        display: false, // Hide axis labels but keep scaling
                        grid: { display: false }
                    }
                }
            }
        });
    }
}


function initPriceVolumeCharts(root = document) {
    const canvas = root.querySelector('#priceVolumeCanvas');
    const dataScript = root.querySelector('#chart-data-source');

    if (!canvas || !dataScript || typeof Chart === 'undefined') return;
    if (canvas.dataset.initialized === 'true') return;

    try {
        const data = JSON.parse(dataScript.textContent);
        new PriceVolumeChart(canvas.id, data);
        canvas.dataset.initialized = 'true';
    } catch (e) {
        console.error('Chart init failed:', e);
    }
}
const isMobile = window.innerWidth < 640;
window.addEventListener('load', () => {
    initPriceVolumeCharts();
});

document.body.addEventListener('htmx:afterSwap', (e) => {
    initPriceVolumeCharts(e.target);
});
