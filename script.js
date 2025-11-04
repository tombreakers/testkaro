// Mobile Navigation Toggle
const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav-links');

burger.addEventListener('click', () => {
    nav.classList.toggle('active');
    burger.classList.toggle('active');
});

// Close mobile menu when clicking on a link
const navLinks = document.querySelectorAll('.nav-links a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
        burger.classList.remove('active');
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // Account for fixed navbar
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.style.padding = '1rem 0';
        navbar.style.boxShadow = '0 2px 30px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.padding = '1.5rem 0';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.05)';
    }

    lastScroll = currentScroll;
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
const animateElements = document.querySelectorAll('.feature-card, .product-card, .testimonial-card');
animateElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Shopify Buy Button Integration
// IMPORTANT: Replace these with your actual Shopify credentials
const shopifyConfig = {
    domain: 'your-store.myshopify.com', // Replace with your Shopify store domain
    storefrontAccessToken: 'your-storefront-access-token', // Replace with your Storefront API access token
    collectionId: 'your-collection-id' // Replace with your collection ID (optional)
};

// Initialize Shopify Buy Button
function initializeShopify() {
    // Check if the Shopify SDK is loaded
    if (typeof ShopifyBuy === 'undefined') {
        console.log('Shopify SDK not loaded yet. Waiting...');
        setTimeout(initializeShopify, 100);
        return;
    }

    // Only initialize if credentials are configured
    if (shopifyConfig.domain === 'your-store.myshopify.com') {
        console.log('⚠️ Shopify not configured. Please update shopifyConfig in script.js with your Shopify credentials.');
        addShopifyInstructions();
        return;
    }

    try {
        const client = ShopifyBuy.buildClient({
            domain: shopifyConfig.domain,
            storefrontAccessToken: shopifyConfig.storefrontAccessToken
        });

        const ui = ShopifyBuy.UI.init(client);

        // Option 1: Load a specific collection
        if (shopifyConfig.collectionId && shopifyConfig.collectionId !== 'your-collection-id') {
            ui.createComponent('collection', {
                id: shopifyConfig.collectionId,
                node: document.getElementById('shopify-collection'),
                options: {
                    product: {
                        styles: {
                            product: {
                                '@media (min-width: 601px)': {
                                    'max-width': 'calc(25% - 20px)',
                                    'margin-left': '20px',
                                    'margin-bottom': '50px',
                                    'width': 'calc(25% - 20px)'
                                },
                                'img': {
                                    'height': '350px',
                                    'object-fit': 'cover'
                                }
                            },
                            title: {
                                'font-family': 'Cormorant Garamond, serif',
                                'font-size': '1.5rem',
                                'color': '#2c2c54'
                            },
                            price: {
                                'font-size': '1.5rem',
                                'color': '#1a1a1a'
                            },
                            button: {
                                'background-color': '#2c2c54',
                                'border-radius': '5px',
                                'padding': '12px',
                                ':hover': {
                                    'background-color': '#d4a5a5'
                                }
                            }
                        }
                    },
                    cart: {
                        styles: {
                            button: {
                                'background-color': '#2c2c54',
                                ':hover': {
                                    'background-color': '#d4a5a5'
                                }
                            }
                        }
                    },
                    toggle: {
                        styles: {
                            toggle: {
                                'background-color': '#2c2c54',
                                ':hover': {
                                    'background-color': '#d4a5a5'
                                }
                            }
                        }
                    }
                }
            });
        } else {
            // Option 2: Load all products
            ui.createComponent('product', {
                node: document.getElementById('shopify-collection'),
                options: {
                    product: {
                        styles: {
                            product: {
                                '@media (min-width: 601px)': {
                                    'max-width': 'calc(25% - 20px)',
                                    'margin-left': '20px',
                                    'margin-bottom': '50px'
                                }
                            }
                        }
                    }
                }
            });
        }

        console.log('✅ Shopify integration initialized successfully!');

    } catch (error) {
        console.error('Error initializing Shopify:', error);
        addShopifyInstructions();
    }
}

// Add instructions for Shopify setup
function addShopifyInstructions() {
    const collectionSection = document.getElementById('shopify-collection');
    if (collectionSection) {
        collectionSection.innerHTML = `
            <div style="background: #f8f7f4; padding: 3rem; border-radius: 10px; text-align: center; max-width: 800px; margin: 0 auto;">
                <h3 style="font-family: 'Cormorant Garamond', serif; font-size: 2rem; color: #2c2c54; margin-bottom: 1rem;">
                    Shopify Integration Setup Required
                </h3>
                <p style="color: #6b6b6b; margin-bottom: 2rem; line-height: 1.8;">
                    To display your products, please configure your Shopify credentials in <code>script.js</code>.
                </p>
                <div style="text-align: left; background: white; padding: 2rem; border-radius: 5px; margin-bottom: 2rem;">
                    <h4 style="margin-bottom: 1rem; color: #2c2c54;">Steps to Configure:</h4>
                    <ol style="line-height: 2; color: #1a1a1a;">
                        <li>Go to your Shopify Admin → Apps → Develop apps</li>
                        <li>Create a new app or select an existing one</li>
                        <li>Configure Storefront API access</li>
                        <li>Copy your Storefront Access Token</li>
                        <li>Update the <code>shopifyConfig</code> object in <code>script.js</code></li>
                    </ol>
                </div>
                <a href="https://shopify.dev/docs/api/storefront" target="_blank"
                   style="display: inline-block; padding: 1rem 2rem; background: #2c2c54; color: white; text-decoration: none; border-radius: 5px; font-weight: 500;">
                    View Shopify Documentation
                </a>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeShopify);
} else {
    initializeShopify();
}

// Product card click handling for sample products
const productButtons = document.querySelectorAll('.product-button');
productButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        e.stopPropagation();
        const productName = button.closest('.product-card').querySelector('.product-name').textContent;

        // If Shopify is not configured, show alert
        if (shopifyConfig.domain === 'your-store.myshopify.com') {
            alert(`Shopify integration required to purchase "${productName}". Please configure your Shopify credentials in script.js.`);
        }
    });
});

// Custom Design button
const customDesignButton = document.querySelector('.cta-button-secondary');
if (customDesignButton) {
    customDesignButton.addEventListener('click', () => {
        if (shopifyConfig.domain === 'your-store.myshopify.com') {
            alert('Custom design feature requires Shopify integration. Please configure your Shopify store first.');
        } else {
            // Redirect to your custom design page or open a modal
            alert('Custom design feature - integrate with your Shopify product customization app here!');
        }
    });
}

// Add parallax effect to hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Add loading animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});
