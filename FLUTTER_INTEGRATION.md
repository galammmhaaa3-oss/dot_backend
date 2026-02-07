# 🎉 Backend Deployed Successfully!

## ✅ Your API is Live

**API URL**: https://dot-api-8fxv.onrender.com

**Endpoints:**
- Health Check: https://dot-api-8fxv.onrender.com/health
- API Documentation: https://dot-api-8fxv.onrender.com/docs
- Alternative Docs: https://dot-api-8fxv.onrender.com/redoc

---

## 📱 Connect Flutter App

Update your Flutter app to use the API:

### 1. Create API Service Class

Create `lib/services/api_service.dart`:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiConfig {
  static const String baseUrl = "https://dot-api-8fxv.onrender.com/api/v1";
}

class ApiService {
  static String? _token;
  
  // Set token after login
  static void setToken(String token) {
    _token = token;
  }
  
  // Get headers with auth
  static Map<String, String> _getHeaders({bool includeAuth = false}) {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    
    return headers;
  }
  
  // Register
  static Future<Map<String, dynamic>> register({
    required String phone,
    required String name,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/register'),
      headers: _getHeaders(),
      body: jsonEncode({
        'phone': phone,
        'name': name,
        'password': password,
      }),
    );
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Registration failed: ${response.body}');
    }
  }
  
  // Login
  static Future<String> login({
    required String phone,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/login'),
      headers: _getHeaders(),
      body: jsonEncode({
        'phone': phone,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'];
      setToken(token);
      return token;
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }
  
  // Create Ride
  static Future<Map<String, dynamic>> createRide({
    required double pickupLat,
    required double pickupLng,
    required String pickupAddress,
    required double destinationLat,
    required double destinationLng,
    required String destinationAddress,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/rides'),
      headers: _getHeaders(includeAuth: true),
      body: jsonEncode({
        'pickup_lat': pickupLat,
        'pickup_lng': pickupLng,
        'pickup_address': pickupAddress,
        'destination_lat': destinationLat,
        'destination_lng': destinationLng,
        'destination_address': destinationAddress,
      }),
    );
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Create ride failed: ${response.body}');
    }
  }
  
  // Create Delivery
  static Future<Map<String, dynamic>> createDelivery({
    required String orderType,
    required double pickupLat,
    required double pickupLng,
    required String pickupAddress,
    String? pickupDetails,
    required String senderName,
    required double deliveryLat,
    required double deliveryLng,
    required String deliveryAddress,
    String? deliveryDetails,
    required String receiverName,
    required String receiverPhone,
    required String receiverNationalId,
    bool driverPays = false,
    double productAmount = 0,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/deliveries'),
      headers: _getHeaders(includeAuth: true),
      body: jsonEncode({
        'order_type': orderType,
        'pickup_lat': pickupLat,
        'pickup_lng': pickupLng,
        'pickup_address': pickupAddress,
        'pickup_details': pickupDetails,
        'sender_name': senderName,
        'delivery_lat': deliveryLat,
        'delivery_lng': deliveryLng,
        'delivery_address': deliveryAddress,
        'delivery_details': deliveryDetails,
        'receiver_name': receiverName,
        'receiver_phone': receiverPhone,
        'receiver_national_id': receiverNationalId,
        'driver_pays': driverPays,
        'product_amount': productAmount,
      }),
    );
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Create delivery failed: ${response.body}');
    }
  }
  
  // Get User Profile
  static Future<Map<String, dynamic>> getUserProfile() async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/users/me'),
      headers: _getHeaders(includeAuth: true),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Get profile failed: ${response.body}');
    }
  }
  
  // Get Ride History
  static Future<List<dynamic>> getRideHistory() async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/rides'),
      headers: _getHeaders(includeAuth: true),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Get rides failed: ${response.body}');
    }
  }
  
  // Get Delivery History
  static Future<List<dynamic>> getDeliveryHistory() async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/deliveries'),
      headers: _getHeaders(includeAuth: true),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Get deliveries failed: ${response.body}');
    }
  }
}
```

### 2. Add HTTP Package

In `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
```

Run:
```bash
flutter pub get
```

### 3. Usage Example

```dart
// Register
try {
  final user = await ApiService.register(
    phone: '0912345678',
    name: 'Test User',
    password: 'password123',
  );
  print('User registered: ${user['id']}');
} catch (e) {
  print('Error: $e');
}

// Login
try {
  final token = await ApiService.login(
    phone: '0912345678',
    password: 'password123',
  );
  print('Logged in! Token: $token');
} catch (e) {
  print('Error: $e');
}

// Create Ride
try {
  final ride = await ApiService.createRide(
    pickupLat: 36.2021,
    pickupLng: 37.1343,
    pickupAddress: 'Aleppo, Syria',
    destinationLat: 36.2100,
    destinationLng: 37.1500,
    destinationAddress: 'Aleppo University',
  );
  print('Ride created! Price: ${ride['estimated_price']} SYP');
} catch (e) {
  print('Error: $e');
}
```

---

## ⚠️ Important Notes

### Free Tier Limitations
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- PostgreSQL is **NOT free** on Render (you'll be charged after trial)

### Database Cost Warning
The PostgreSQL database will cost **$7/month** after the free trial ends.

**Free Alternative:** Use **Neon.tech** for free PostgreSQL:
1. Go to https://neon.tech
2. Create free account
3. Create database
4. Copy connection string
5. In Render → dot-api → Environment → Edit `DATABASE_URL`
6. Delete the Render PostgreSQL database

---

## 🧪 Test Your API Now

Open: https://dot-api-8fxv.onrender.com/docs

Try:
1. **Register** a new user
2. **Login** to get token
3. Click **Authorize** (top right)
4. Paste token
5. **Create a ride** or **delivery**!

---

## 🎯 Next Steps

1. ✅ Backend is live
2. 📱 Add API service to Flutter app
3. 🧪 Test all features
4. 🚀 Launch your app!

**Congratulations! Your backend is ready!** 🎉
