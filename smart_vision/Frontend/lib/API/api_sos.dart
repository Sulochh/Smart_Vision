import 'package:dio/dio.dart';
import 'package:geolocator/geolocator.dart';

Future<void> apiSOS() async {
  print("API SOS");
  // Step 1: Get current location
  bool serviceEnabled;
  LocationPermission permission;

  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    print("Location services are disabled.");
    return;
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      print("Location permissions are denied");
      return;
    }
  }

  if (permission == LocationPermission.deniedForever) {
    print("Location permissions are permanently denied");
    return;
  }

  Position position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high);
  String locationUrl =
      "https://maps.google.com/?q=${position.latitude},${position.longitude}";

  // Step 2: Make API call with location in message

  print(locationUrl);
  Response response;
  var dio = Dio();
  response = await dio.post(
    'http://192.168.1.4:5000/sos',
    data: {
      'data': [
        "7305981218"
      ],
      'message': "SOS EMERGENCY. I need help.\nLocation: $locationUrl"
    },
  );

  print(response.data.toString());
}



/*
Future<void> apiSOS() async {
  print("API SOS");
  Response response;
  var dio = Dio();
  response = await dio.post('http://192.168.163.146:5000/sos', data: {
    'data': [
      "7305981218"
    ],
  });
  print(response.data.toString());
}
*/