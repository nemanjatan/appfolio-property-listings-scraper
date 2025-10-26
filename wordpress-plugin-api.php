<?php
/**
 * Plugin Name: AppFolio Properties API
 * Description: Displays property listings from AppFolio API
 * Version: 1.0.0
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class AppFolioPropertiesAPI {
    private $api_url;
    
    public function __construct() {
        // Set your API URL here (Railway will provide this)
        $this->api_url = get_option('appfolio_api_url', 'https://your-api-url.up.railway.app');
        
        // Register shortcode
        add_shortcode('appfolio_properties', array($this, 'display_properties'));
        
        // Add admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Enqueue styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }
    
    public function enqueue_styles() {
        wp_enqueue_style('appfolio-properties', plugin_dir_url(__FILE__) . 'assets/style.css');
    }
    
    public function add_admin_menu() {
        add_options_page(
            'AppFolio API Settings',
            'AppFolio API',
            'manage_options',
            'appfolio-api',
            array($this, 'admin_page')
        );
    }
    
    public function admin_page() {
        if (isset($_POST['appfolio_api_url'])) {
            update_option('appfolio_api_url', sanitize_text_field($_POST['appfolio_api_url']));
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        
        $api_url = get_option('appfolio_api_url', '');
        ?>
        <div class="wrap">
            <h1>AppFolio API Settings</h1>
            <form method="post">
                <table class="form-table">
                    <tr>
                        <th scope="row">API URL</th>
                        <td>
                            <input type="url" name="appfolio_api_url" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
                            <p class="description">Enter your Railway API URL (e.g., https://your-app.up.railway.app)</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    public function get_properties($filters = array()) {
        $url = $this->api_url . '/api/properties';
        
        // Add query parameters if filters are provided
        if (!empty($filters)) {
            $url .= '?' . http_build_query($filters);
        }
        
        $response = wp_remote_get($url, array(
            'timeout' => 15,
            'headers' => array(
                'Accept' => 'application/json'
            )
        ));
        
        if (is_wp_error($response)) {
            return array('success' => false, 'error' => $response->get_error_message());
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        return $data;
    }
    
    public function display_properties($atts) {
        $atts = shortcode_atts(array(
            'min_price' => '',
            'max_price' => '',
            'bedrooms' => '',
            'bathrooms' => '',
            'search' => '',
            'limit' => '20'
        ), $atts);
        
        // Build filters
        $filters = array();
        if (!empty($atts['min_price'])) $filters['min_price'] = intval($atts['min_price']);
        if (!empty($atts['max_price'])) $filters['max_price'] = intval($atts['max_price']);
        if (!empty($atts['bedrooms'])) $filters['bedrooms'] = intval($atts['bedrooms']);
        if (!empty($atts['bathrooms'])) $filters['bathrooms'] = floatval($atts['bathrooms']);
        if (!empty($atts['search'])) $filters['search'] = sanitize_text_field($atts['search']);
        
        // Get properties from API
        $result = $this->get_properties($filters);
        
        if (!$result || !$result['success']) {
            return '<div class="appfolio-error">Unable to load properties. Please check API connection.</div>';
        }
        
        $properties = $result['data'];
        
        // Limit results
        if (!empty($atts['limit'])) {
            $properties = array_slice($properties, 0, intval($atts['limit']));
        }
        
        // Display properties
        ob_start();
        ?>
        <div class="appfolio-properties">
            <div class="appfolio-grid">
                <?php foreach ($properties as $property): ?>
                    <div class="appfolio-property-card">
                        <?php if (!empty($property['featured_image'])): ?>
                            <div class="appfolio-image">
                                <img src="<?php echo esc_url($property['featured_image']); ?>" alt="<?php echo esc_attr($property['title']); ?>" />
                            </div>
                        <?php endif; ?>
                        
                        <div class="appfolio-content">
                            <h3 class="appfolio-title"><?php echo esc_html($property['title']); ?></h3>
                            
                            <?php if (!empty($property['address'])): ?>
                                <p class="appfolio-address"><?php echo esc_html($property['address']); ?></p>
                            <?php endif; ?>
                            
                            <?php if (!empty($property['price'])): ?>
                                <p class="appfolio-price">$<?php echo esc_html(number_format($property['price'])); ?>/month</p>
                            <?php endif; ?>
                            
                            <div class="appfolio-details">
                                <?php if (!empty($property['bedrooms'])): ?>
                                    <span class="appfolio-detail"><?php echo esc_html($property['bedrooms']); ?> Beds</span>
                                <?php endif; ?>
                                
                                <?php if (!empty($property['bathrooms'])): ?>
                                    <span class="appfolio-detail"><?php echo esc_html($property['bathrooms']); ?> Baths</span>
                                <?php endif; ?>
                                
                                <?php if (!empty($property['square_feet'])): ?>
                                    <span class="appfolio-detail"><?php echo esc_html(number_format($property['square_feet'])); ?> sq ft</span>
                                <?php endif; ?>
                            </div>
                            
                            <?php if (!empty($property['original_url'])): ?>
                                <a href="<?php echo esc_url($property['original_url']); ?>" class="appfolio-button" target="_blank">View Details</a>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
}

// Initialize the plugin
new AppFolioPropertiesAPI();

