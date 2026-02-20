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
                'brand-bg': '#FFFFFF',
                'brand-sidebar': '#FAFAFA',
                'brand-text-primary': '#333333',
                'brand-text-secondary': '#666666',
                'brand-border': '#E5E5E5',
                'brand-success': '#28A745',
                'brand-primary': '#007BFF',
                'brand-danger': '#DC3545',
            }
        },
    },
    plugins: [],
}
