/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                inter: ['Inter', 'sans-serif'],
            },
            colors: {
                'brand-bg': '#F9FAFB', // Very subtle off-white background
                'brand-sidebar': '#FFFFFF',
                'brand-text-primary': '#111827', // Crisp, dark gray/black
                'brand-text-secondary': '#6B7280', // Medium gray for hierarchy
                'brand-border': '#E5E7EB', // Faint divider borders
                'brand-success': '#111827', // Map success to primary dark for UI consistency unless critical
                'brand-primary': '#111827', // Primary buttons are now black
                'brand-danger': '#EF4444', // Keep red for destructive actions only

                // Pastel accents for Calendar Events
                'event-green': '#D1FAE5',
                'event-blue': '#DBEAFE',
                'event-pink': '#FCE7F3',
                'event-gray': '#F3F4F6'
            }
        },
    },
    plugins: [],
}
