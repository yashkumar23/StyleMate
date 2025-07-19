from flask import Blueprint, request, jsonify
from datetime import datetime

blog_bp = Blueprint('blog', __name__)

# Sample blog posts data (in a real application, this would come from a database)
blog_posts = [
    {
        "id": 1,
        "title": "Spring 2024: Pastel Colors Are Making a Comeback",
        "summary": "Discover how soft pastels are dominating the fashion scene this spring. From lavender blazers to mint green accessories, learn how to incorporate these trending colors into your wardrobe.",
        "content": "Spring 2024 brings a refreshing wave of pastel colors that are taking the fashion world by storm. This season, we're seeing a beautiful resurgence of soft, muted tones that add a touch of elegance and femininity to any wardrobe...",
        "category": "Color Trends",
        "date": "2024-03-15",
        "image": "/blog-images/pastel-trends.jpg",
        "readTime": "5 min read",
        "views": 1250,
        "likes": 89,
        "author": "StyleMate Team",
        "published": True
    },
    {
        "id": 2,
        "title": "Sustainable Fashion: Building an Eco-Friendly Wardrobe",
        "summary": "Learn how to create a sustainable wardrobe without compromising on style. We explore eco-friendly brands, timeless pieces, and tips for reducing your fashion footprint.",
        "content": "Sustainable fashion is no longer just a trend—it's a movement that's reshaping the entire industry. As consumers become more conscious of their environmental impact, the demand for eco-friendly fashion options continues to grow...",
        "category": "Sustainability",
        "date": "2024-03-12",
        "image": "/blog-images/sustainable-fashion.jpg",
        "readTime": "7 min read",
        "views": 2100,
        "likes": 156,
        "author": "StyleMate Team",
        "published": True
    },
    {
        "id": 3,
        "title": "Body Type Styling: Dressing for Your Apple Shape",
        "summary": "Expert tips and tricks for apple-shaped body types. Discover the best silhouettes, patterns, and styling techniques to enhance your natural beauty and boost confidence.",
        "content": "Understanding your body type is the key to building a wardrobe that makes you look and feel your best. For apple-shaped body types, the goal is to create balance and highlight your best features...",
        "category": "Body Styling",
        "date": "2024-03-10",
        "image": "/blog-images/apple-body-styling.jpg",
        "readTime": "6 min read",
        "views": 1800,
        "likes": 134,
        "author": "StyleMate Team",
        "published": True
    },
    {
        "id": 4,
        "title": "Accessory Trends 2024: Statement Jewelry Takes Center Stage",
        "summary": "From chunky gold chains to colorful resin earrings, explore the accessory trends that are defining 2024. Learn how to style statement pieces for maximum impact.",
        "content": "2024 is the year of bold, statement-making accessories. Gone are the days of subtle, understated jewelry—this year, it's all about pieces that command attention and express your personality...",
        "category": "Accessories",
        "date": "2024-03-08",
        "image": "/blog-images/statement-jewelry.jpg",
        "readTime": "4 min read",
        "views": 950,
        "likes": 67,
        "author": "StyleMate Team",
        "published": True
    },
    {
        "id": 5,
        "title": "Workplace Fashion: Professional Looks That Make an Impact",
        "summary": "Elevate your professional wardrobe with these modern workplace fashion tips. From power dressing to business casual, find your perfect office style.",
        "content": "The modern workplace has evolved, and so has professional fashion. Today's office attire is about finding the perfect balance between professionalism and personal style...",
        "category": "Professional",
        "date": "2024-03-05",
        "image": "/blog-images/workplace-fashion.jpg",
        "readTime": "8 min read",
        "views": 1650,
        "likes": 112,
        "author": "StyleMate Team",
        "published": True
    }
]

@blog_bp.route('/api/blog/posts', methods=['GET'])
def get_blog_posts():
    """Get all published blog posts"""
    try:
        # Filter only published posts and sort by date (newest first)
        published_posts = [post for post in blog_posts if post.get('published', False)]
        published_posts.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'posts': published_posts,
            'total': len(published_posts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching blog posts'
        }), 500

@blog_bp.route('/api/blog/posts/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    """Get a specific blog post by ID"""
    try:
        post = next((post for post in blog_posts if post['id'] == post_id and post.get('published', False)), None)
        
        if not post:
            return jsonify({
                'success': False,
                'message': 'Blog post not found'
            }), 404
        
        # Increment view count (in a real app, this would be saved to database)
        post['views'] += 1
        
        return jsonify({
            'success': True,
            'post': post
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching blog post'
        }), 500

@blog_bp.route('/api/blog/posts/<int:post_id>/like', methods=['POST'])
def like_blog_post(post_id):
    """Like a blog post"""
    try:
        post = next((post for post in blog_posts if post['id'] == post_id and post.get('published', False)), None)
        
        if not post:
            return jsonify({
                'success': False,
                'message': 'Blog post not found'
            }), 404
        
        # Increment like count (in a real app, this would be saved to database)
        post['likes'] += 1
        
        return jsonify({
            'success': True,
            'message': 'Post liked successfully',
            'likes': post['likes']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error liking blog post'
        }), 500

@blog_bp.route('/api/blog/categories', methods=['GET'])
def get_blog_categories():
    """Get all blog categories"""
    try:
        categories = list(set(post['category'] for post in blog_posts if post.get('published', False)))
        categories.sort()
        
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching categories'
        }), 500

@blog_bp.route('/api/blog/posts/category/<category>', methods=['GET'])
def get_posts_by_category(category):
    """Get blog posts by category"""
    try:
        filtered_posts = [post for post in blog_posts 
                         if post.get('published', False) and post['category'].lower() == category.lower()]
        filtered_posts.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'posts': filtered_posts,
            'category': category,
            'total': len(filtered_posts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching posts by category'
        }), 500

# Admin routes for managing blog posts (in a real app, these would require authentication)
@blog_bp.route('/api/blog/admin/posts', methods=['POST'])
def create_blog_post():
    """Create a new blog post (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'summary', 'content', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        # Generate new ID
        new_id = max(post['id'] for post in blog_posts) + 1 if blog_posts else 1
        
        # Create new post
        new_post = {
            'id': new_id,
            'title': data['title'],
            'summary': data['summary'],
            'content': data['content'],
            'category': data['category'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'image': data.get('image', '/blog-images/default.jpg'),
            'readTime': data.get('readTime', '5 min read'),
            'views': 0,
            'likes': 0,
            'author': data.get('author', 'StyleMate Team'),
            'published': data.get('published', True)
        }
        
        blog_posts.append(new_post)
        
        return jsonify({
            'success': True,
            'message': 'Blog post created successfully',
            'post': new_post
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error creating blog post'
        }), 500

