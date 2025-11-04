# Silk & Slumber - Luxury Custom Silk Pajamas

A visually engaging, classy e-commerce website for selling custom-designed silk pajamas, integrated with Shopify for seamless payment processing and inventory management.

## Features

- **Elegant Design**: Luxury-focused aesthetics with smooth animations and modern UI
- **Shopify Integration**: Seamless integration with Shopify's Buy Button SDK for product display and checkout
- **Responsive Layout**: Fully responsive design that works beautifully on all devices
- **Custom Design Showcase**: Dedicated section highlighting custom design capabilities
- **Product Collection**: Grid-based product display with hover effects
- **Interactive Elements**: Smooth scrolling, animated sections, and mobile-friendly navigation
- **Professional Branding**: Sophisticated typography and color scheme

## Tech Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with custom properties, Grid, and Flexbox
- **JavaScript**: Vanilla JS for interactions and Shopify SDK integration
- **Shopify Buy Button SDK**: For e-commerce functionality

## Getting Started

### 1. Clone or Download

```bash
git clone <your-repo-url>
cd testkaro
```

### 2. Open Locally

Simply open `index.html` in your web browser to view the site locally:

```bash
# On macOS
open index.html

# On Linux
xdg-open index.html

# On Windows
start index.html
```

### 3. Configure Shopify Integration

To connect your Shopify store and enable product display/purchasing:

#### Step 1: Create a Shopify App

1. Log into your Shopify Admin panel
2. Navigate to **Settings** → **Apps and sales channels** → **Develop apps**
3. Click **Create an app** (or select an existing app)
4. Give your app a name (e.g., "Silk & Slumber Website")

#### Step 2: Configure Storefront API

1. In your app settings, go to **Configuration**
2. Under **Storefront API**, click **Configure**
3. Enable the following scopes:
   - `unauthenticated_read_product_listings`
   - `unauthenticated_read_product_inventory`
   - `unauthenticated_read_product_tags`
   - `unauthenticated_read_collection_listings`
4. Click **Save**

#### Step 3: Get Your Credentials

1. Go to **API credentials** tab
2. Under **Storefront API access token**, click **Install app**
3. Copy the **Storefront API access token** (you'll only see this once)
4. Your **domain** is your store URL (e.g., `your-store.myshopify.com`)

#### Step 4: Update Configuration

Open `script.js` and update the `shopifyConfig` object with your credentials:

```javascript
const shopifyConfig = {
    domain: 'your-store.myshopify.com',              // Your Shopify store domain
    storefrontAccessToken: 'your-storefront-token',   // Your Storefront API access token
    collectionId: 'your-collection-id'                // (Optional) Specific collection ID
};
```

#### Step 5: Get Collection ID (Optional)

To display a specific collection of products:

1. In Shopify Admin, go to **Products** → **Collections**
2. Click on the collection you want to display
3. The collection ID is in the URL: `admin.shopify.com/store/your-store/collections/[COLLECTION_ID]`
4. Use this ID in the `collectionId` field

Alternatively, leave `collectionId` as `'your-collection-id'` to display all products.

## File Structure

```
testkaro/
├── index.html          # Main HTML file
├── styles.css          # All styling and animations
├── script.js           # JavaScript functionality and Shopify integration
└── README.md          # This file
```

## Customization

### Colors

The site uses CSS custom properties for easy theming. Update these in `styles.css`:

```css
:root {
    --primary-color: #2c2c54;      /* Main brand color */
    --secondary-color: #d4a5a5;    /* Accent color */
    --accent-color: #9b8ea0;       /* Additional accent */
    --text-dark: #1a1a1a;          /* Dark text */
    --text-light: #6b6b6b;         /* Light text */
    --bg-light: #f8f7f4;           /* Light background */
    --gold: #d4af37;               /* Gold accents */
}
```

### Fonts

The site uses:
- **Cormorant Garamond**: Display font for headings
- **Montserrat**: Body font for readable text

Change fonts in `styles.css` by updating the Google Fonts import and CSS variables.

### Products

The sample products shown are placeholders. Once Shopify is configured, they will be supplemented/replaced by your actual Shopify products.

To customize placeholder products, edit the product cards in `index.html`.

## Deployment

### Option 1: GitHub Pages

1. Push your code to GitHub
2. Go to repository **Settings** → **Pages**
3. Select your branch and click **Save**
4. Your site will be live at `https://yourusername.github.io/testkaro/`

### Option 2: Netlify

1. Create a free account at [Netlify](https://netlify.com)
2. Drag and drop your project folder
3. Your site will be deployed instantly with a custom URL

### Option 3: Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in your project directory
3. Follow the prompts to deploy

### Option 4: Traditional Web Hosting

Upload all files to your web hosting provider via FTP or their file manager.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Features Breakdown

### Navigation
- Fixed header with smooth scrolling
- Mobile-responsive hamburger menu
- Scroll-based navbar effects

### Hero Section
- Full-screen gradient background with animations
- Call-to-action button
- Scroll indicator

### Product Grid
- Responsive grid layout
- Hover effects and transitions
- Product badges (New, Popular, Limited)
- Shopify integration ready

### Custom Design Section
- Split-screen layout
- Animated design layers visualization
- Feature list with custom checkmarks

### Testimonials
- Grid-based layout
- Star ratings
- Hover effects

### Footer
- Multi-column layout
- Social media links
- Site navigation

## Shopify Features

Once configured, the site will:
- Display your products automatically
- Show real-time pricing and inventory
- Handle cart management
- Process checkout through Shopify
- Support product variants (sizes, colors)
- Update automatically when you add/remove products in Shopify

## Advanced Shopify Integration

### Product Customization

For custom design functionality, consider integrating:
- [Shopify Product Customizer apps](https://apps.shopify.com/browse/product-customization)
- Custom file upload functionality
- Design preview tools

### Additional Features

You can enhance the integration with:
- Customer accounts
- Wishlist functionality
- Product reviews
- Email marketing integration
- Analytics tracking

## Support & Documentation

- [Shopify Storefront API Docs](https://shopify.dev/docs/api/storefront)
- [Shopify Buy Button SDK](https://shopify.github.io/buy-button-js/)
- [Shopify Developer Portal](https://shopify.dev/)

## License

This project is available for personal and commercial use.

## Credits

- Design & Development: Custom built for Silk & Slumber
- Fonts: Google Fonts (Cormorant Garamond, Montserrat)
- Icons: Hand-coded SVG icons
- E-commerce: Shopify Platform

---

**Need Help?** Check the Shopify documentation or create an issue in this repository.
