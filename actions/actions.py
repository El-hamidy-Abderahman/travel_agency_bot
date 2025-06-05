from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import json
import requests
from datetime import datetime, timedelta

# Global conversation storage
conversations = {}

class FlightAPI:
    """Real Flight API Integration - Using Amadeus API"""
    
    def __init__(self):
        # You need to register at https://developers.amadeus.com/ to get these
        self.client_id = "YOUR_AMADEUS_CLIENT_ID"
        self.client_secret = "YOUR_AMADEUS_CLIENT_SECRET"
        self.base_url = "https://test.api.amadeus.com"
        self.access_token = None
    
    def get_access_token(self):
        """Get OAuth token from Amadeus"""
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return True
        except Exception as e:
            print(f"Error getting access token: {e}")
        return False
    
    def search_flights(self, departure_city: str, destination_city: str, departure_date: str, 
                      trip_type: str = "ذهاب وإياب", flight_class: str = "اقتصادية"):
        """Search flights using Amadeus Flight Offers Search API"""
        
        print(f"Searching flights from {departure_city} to {destination_city}")
        
        # For now, return fallback data since API setup requires credentials
        # In production, implement the real API call here
        return self._fallback_flights(departure_city, destination_city, departure_date, trip_type, flight_class)
    
    def _fallback_flights(self, departure_city, destination_city, departure_date, trip_type, flight_class):
        """Fallback flights when API fails or for demo purposes"""
        print("Using fallback flight data")
        return [
            {
                "airline": "الخطوط الملكية المغربية",
                "flight_number": "AT123",
                "departure": departure_city,
                "destination": destination_city,
                "departure_time": "10:00",
                "arrival_time": "12:30",
                "price": "2500 درهم",
                "class": flight_class,
                "date": departure_date
            },
            {
                "airline": "طيران العربية", 
                "flight_number": "3O456",
                "departure": departure_city,
                "destination": destination_city,
                "departure_time": "15:30",
                "arrival_time": "18:00",
                "price": "1800 درهم",
                "class": flight_class,
                "date": departure_date
            }
        ]

class HotelAPI:
    """Real Hotel API Integration - Using Booking.com API"""
    
    def __init__(self):
        self.api_key = "YOUR_BOOKING_API_KEY"
        self.base_url = "https://distribution-xml.booking.com/json/bookings"
    
    def search_hotels(self, city: str, category: str, district: str, number_of_people: str):
        """Search hotels using Booking.com API"""
        
        print(f"Searching hotels in {city}, category: {category}")
        
        # For now, return fallback data since API setup requires credentials
        # In production, implement the real API call here
        return self._fallback_hotels(city, category, district, number_of_people)
    
    def _fallback_hotels(self, city, category, district, number_of_people):
        """Fallback hotels when API fails or for demo purposes"""
        print("Using fallback hotel data")
        return [
            {
                "name": f"فندق {city} الملكي",
                "category": category,
                "city": city,
                "district": district,
                "price": "800 درهم / ليلة",
                "amenities": "مسبح، سبا، واي فاي مجاني",
                "rating": "4.8/5"
            },
            {
                "name": f"منتجع {city} الذهبي",
                "category": category,
                "city": city, 
                "district": district,
                "price": "650 درهم / ليلة",
                "amenities": "مطعم، صالة رياضة، موقف سيارات",
                "rating": "4.5/5"
            }
        ]

# Initialize API instances
flight_api = FlightAPI()
hotel_api = HotelAPI()

class ActionSearchFlight(Action):
    def name(self) -> Text:
        return "action_search_flight"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        print(f"DEBUG - ActionSearchFlight for sender: {sender_id}")
        
        if sender_id not in conversations:
            conversations[sender_id] = {}
        
        conv_data = conversations[sender_id]
        print(f"DEBUG - Current conversation data: {conv_data}")
        
        # Check what we still need to collect
        if 'departure_city' not in conv_data:
            dispatcher.utter_message(text="من أي مدينة ترغب بالمغادرة؟ (مثال: مراكش، الرباط، الدار البيضاء)")
            conv_data['next_question'] = 'departure_city'
            conv_data['booking_type'] = 'flight'
            return []
        
        if 'destination_city' not in conv_data:
            dispatcher.utter_message(text="إلى أي مدينة ترغب بالسفر؟ (مثال: باريس، لندن، مدريد)")
            conv_data['next_question'] = 'destination_city'
            return []
        
        if 'departure_date' not in conv_data:
            dispatcher.utter_message(text="ما هو تاريخ المغادرة المفضل لديك؟ (مثال: 15 يونيو، غدا)")
            conv_data['next_question'] = 'departure_date'
            return []
        
        if 'trip_type' not in conv_data:
            dispatcher.utter_message(text="ما نوع الرحلة التي تريدها؟\n• ذهاب وإياب\n• ذهاب فقط")
            conv_data['next_question'] = 'trip_type'
            return []
        
        if 'flight_class' not in conv_data:
            dispatcher.utter_message(text="ما هي درجة السفر التي تفضلها؟\n• اقتصادية\n• رجال أعمال\n• درجة أولى")
            conv_data['next_question'] = 'flight_class'
            return []
        
        # All data collected - call API
        print("DEBUG - All data collected, calling flight API")
        dispatcher.utter_message(text="🔍 جاري البحث عن أفضل الرحلات المتاحة...")
        
        try:
            flights = flight_api.search_flights(
                conv_data['departure_city'],
                conv_data['destination_city'], 
                conv_data['departure_date'],
                conv_data['trip_type'],
                conv_data['flight_class']
            )
            
            if flights:
                response = f"وجدت لك هذه الرحلات المتاحة لـ{conv_data['trip_type']}:\n\n"
                for i, flight in enumerate(flights, 1):
                    response += f"{i}. {flight['airline']} - رحلة رقم {flight['flight_number']}\n"
                    response += f"   من {flight['departure']} إلى {flight['destination']}\n"
                    response += f"   التاريخ: {flight['date']}\n"
                    response += f"   المغادرة: {flight['departure_time']} - الوصول: {flight['arrival_time']}\n"
                    response += f"   الدرجة: {flight['class']} - السعر: {flight['price']}\n\n"
                
                response += "أي من هذه الرحلات تناسبك؟ اكتب 'الخيار الأول' أو 'الخيار الثاني'."
                
                # Store available flights for selection
                conv_data['available_flights'] = flights
                conv_data['next_question'] = 'flight_selection'
                conv_data['booking_type'] = 'flight'
                
            else:
                response = "عذراً، لم أجد رحلات متاحة لهذا التاريخ. هل تريد تجربة تاريخ آخر؟"
                
        except Exception as e:
            print(f"Error in flight search: {e}")
            response = "حدث خطأ في البحث عن الرحلات. يرجى المحاولة مرة أخرى."
        
        dispatcher.utter_message(text=response)
        return []

class ActionSearchHotel(Action):
    def name(self) -> Text:
        return "action_search_hotel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        print(f"DEBUG - ActionSearchHotel for sender: {sender_id}")
        
        if sender_id not in conversations:
            conversations[sender_id] = {}
        
        conv_data = conversations[sender_id]
        
        # Check what we still need to collect for hotel booking
        if 'hotel_city' not in conv_data:
            dispatcher.utter_message(text="في أي مدينة تريد حجز الفندق؟ (مثال: مراكش، الرباط، الدار البيضاء)")
            conv_data['next_question'] = 'hotel_city'
            conv_data['booking_type'] = 'hotel'
            return []
        
        if 'hotel_category' not in conv_data:
            dispatcher.utter_message(text="ما هي فئة الفندق التي تفضلها؟\n• 5 نجوم\n• 4 نجوم\n• 3 نجوم")
            conv_data['next_question'] = 'hotel_category'
            return []
        
        if 'number_of_people' not in conv_data:
            dispatcher.utter_message(text="كم عدد الأشخاص؟ (مثال: شخص واحد، شخصين، 3 أشخاص)")
            conv_data['next_question'] = 'number_of_people'
            return []
        
        if 'hotel_district' not in conv_data:
            dispatcher.utter_message(text="في أي منطقة تفضل الإقامة؟\n• وسط المدينة\n• المدينة القديمة\n• قريب من المطار\n• المنطقة السياحية")
            conv_data['next_question'] = 'hotel_district'
            return []
        
        # All data collected - call API
        print("DEBUG - All hotel data collected, calling hotel API")
        dispatcher.utter_message(text="🔍 جاري البحث عن أفضل الفنادق المتاحة...")
        
        try:
            hotels = hotel_api.search_hotels(
                conv_data['hotel_city'],
                conv_data['hotel_category'],
                conv_data['hotel_district'],
                conv_data['number_of_people']
            )
            
            if hotels:
                response = f"وجدت لك هذه الفنادق المتاحة في {conv_data['hotel_city']} لـ{conv_data['number_of_people']}:\n\n"
                for i, hotel in enumerate(hotels, 1):
                    response += f"{i}. {hotel['name']} - {hotel['category']}\n"
                    response += f"   الموقع: {hotel['district']} - {hotel['city']}\n"
                    response += f"   السعر: {hotel['price']}\n"
                    response += f"   الخدمات: {hotel['amenities']}\n"
                    response += f"   التقييم: {hotel['rating']}\n\n"
                
                response += "أي من هذه الفنادق يناسبك؟ اكتب 'الخيار الأول' أو 'الخيار الثاني'."
                
                # Store available hotels for selection
                conv_data['available_hotels'] = hotels
                conv_data['next_question'] = 'hotel_selection'
                
            else:
                response = "عذراً، لم أجد فنادق متاحة لهذه المعايير. هل تريد تعديل البحث؟"
                
        except Exception as e:
            print(f"Error in hotel search: {e}")
            response = "حدث خطأ في البحث عن الفنادق. يرجى المحاولة مرة أخرى."
        
        dispatcher.utter_message(text=response)
        return []

class ActionProcessUserInput(Action):
    def name(self) -> Text:
        return "action_process_user_input"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        user_message = tracker.latest_message.get('text', '').strip()
        
        print(f"DEBUG - ActionProcessUserInput for sender: {sender_id}")
        print(f"DEBUG - User message: '{user_message}'")
        
        if sender_id not in conversations:
            conversations[sender_id] = {}
        
        conv_data = conversations[sender_id]
        next_question = conv_data.get('next_question')
        
        print(f"DEBUG - Next question: {next_question}")
        
        # Process based on what we're expecting
        if next_question == 'departure_city':
            city = self._extract_city_from_message(user_message) or user_message
            conv_data['departure_city'] = city
            print(f"DEBUG - Set departure_city to: {city}")
            return [FollowupAction("action_search_flight")]
        
        elif next_question == 'destination_city':
            city = self._extract_city_from_message(user_message) or user_message
            conv_data['destination_city'] = city
            print(f"DEBUG - Set destination_city to: {city}")
            return [FollowupAction("action_search_flight")]
        
        elif next_question == 'departure_date':
            conv_data['departure_date'] = user_message
            print(f"DEBUG - Set departure_date to: {user_message}")
            return [FollowupAction("action_search_flight")]
        
        elif next_question == 'trip_type':
            trip_type = self._extract_trip_type(user_message)
            conv_data['trip_type'] = trip_type
            print(f"DEBUG - Set trip_type to: {trip_type}")
            return [FollowupAction("action_search_flight")]
        
        elif next_question == 'flight_class':
            flight_class = self._extract_flight_class(user_message)
            conv_data['flight_class'] = flight_class
            print(f"DEBUG - Set flight_class to: {flight_class}")
            return [FollowupAction("action_search_flight")]
        
        # Handle flight selection
        elif next_question == 'flight_selection':
            selected_index = self._extract_option_number(user_message)
            if selected_index is not None and 'available_flights' in conv_data:
                if 0 <= selected_index < len(conv_data['available_flights']):
                    selected_flight = conv_data['available_flights'][selected_index]
                    conv_data['booking_summary'] = selected_flight
                    
                    # Show booking summary and ask for confirmation
                    response = f"📋 ملخص حجز الرحلة:\n\n"
                    response += f"• شركة الطيران: {selected_flight['airline']}\n"
                    response += f"• رقم الرحلة: {selected_flight['flight_number']}\n"
                    response += f"• من {selected_flight['departure']} إلى {selected_flight['destination']}\n"
                    response += f"• التاريخ: {selected_flight['date']}\n"
                    response += f"• وقت المغادرة: {selected_flight['departure_time']}\n"
                    response += f"• وقت الوصول: {selected_flight['arrival_time']}\n"
                    response += f"• الدرجة: {selected_flight['class']}\n"
                    response += f"• السعر: {selected_flight['price']}\n\n"
                    response += "هل تريد تأكيد هذا الحجز أم تفضل تغيير الاختيار؟\n"
                    response += "اكتب 'أؤكد الحجز' للتأكيد أو 'أريد تغيير' للتعديل."
                    
                    conv_data['next_question'] = 'confirm_or_change'
                    dispatcher.utter_message(text=response)
                    return []
            
            dispatcher.utter_message(text="من فضلك اختر 'الخيار الأول' أو 'الخيار الثاني'.")
            return []
        
        # Handle hotel selection
        elif next_question == 'hotel_selection':
            selected_index = self._extract_option_number(user_message)
            if selected_index is not None and 'available_hotels' in conv_data:
                if 0 <= selected_index < len(conv_data['available_hotels']):
                    selected_hotel = conv_data['available_hotels'][selected_index]
                    conv_data['booking_summary'] = selected_hotel
                    
                    # Show booking summary and ask for confirmation
                    response = f"📋 ملخص حجز الفندق:\n\n"
                    response += f"• اسم الفندق: {selected_hotel['name']}\n"
                    response += f"• الفئة: {selected_hotel['category']}\n"
                    response += f"• الموقع: {selected_hotel['district']} - {selected_hotel['city']}\n"
                    response += f"• عدد الأشخاص: {conv_data.get('number_of_people', 'غير محدد')}\n"
                    response += f"• السعر: {selected_hotel['price']}\n"
                    response += f"• الخدمات: {selected_hotel['amenities']}\n"
                    response += f"• التقييم: {selected_hotel['rating']}\n\n"
                    response += "هل تريد تأكيد هذا الحجز أم تفضل تغيير الاختيار؟\n"
                    response += "اكتب 'أؤكد الحجز' للتأكيد أو 'أريد تغيير' للتعديل."
                    
                    conv_data['next_question'] = 'confirm_or_change'
                    dispatcher.utter_message(text=response)
                    return []
            
            dispatcher.utter_message(text="من فضلك اختر 'الخيار الأول' أو 'الخيار الثاني'.")
            return []
        
        # Handle confirmation or change request
        elif next_question == 'confirm_or_change':
            if 'أؤكد' in user_message or 'تأكيد' in user_message or 'موافق' in user_message:
                return [FollowupAction("action_confirm_reservation")]
            elif 'تغيير' in user_message or 'تعديل' in user_message:
                return [FollowupAction("action_update_booking")]
            else:
                dispatcher.utter_message(text="من فضلك اكتب 'أؤكد الحجز' للتأكيد أو 'أريد تغيير' للتعديل.")
                return []
        
        # Hotel booking questions
        elif next_question == 'hotel_city':
            city = self._extract_city_from_message(user_message) or user_message
            conv_data['hotel_city'] = city
            print(f"DEBUG - Set hotel_city to: {city}")
            return [FollowupAction("action_search_hotel")]
        
        elif next_question == 'hotel_category':
            category = self._extract_hotel_category(user_message)
            conv_data['hotel_category'] = category
            print(f"DEBUG - Set hotel_category to: {category}")
            return [FollowupAction("action_search_hotel")]
        
        elif next_question == 'number_of_people':
            people = self._extract_number_of_people(user_message)
            conv_data['number_of_people'] = people
            print(f"DEBUG - Set number_of_people to: {people}")
            return [FollowupAction("action_search_hotel")]
        
        elif next_question == 'hotel_district':
            district = self._extract_hotel_district(user_message)
            conv_data['hotel_district'] = district
            print(f"DEBUG - Set hotel_district to: {district}")
            return [FollowupAction("action_search_hotel")]
        
        else:
            print("DEBUG - No next_question, checking for entities or general processing")
            return []
    
    def _extract_option_number(self, message: str) -> int:
        """Extract option number from user message"""
        if 'الأول' in message or 'الخيار الأول' in message or '1' in message:
            return 0
        elif 'الثاني' in message or 'الخيار الثاني' in message or '2' in message:
            return 1
        elif 'الثالث' in message or 'الخيار الثالث' in message or '3' in message:
            return 2
        return None
    
    def _extract_city_from_message(self, message: str) -> str:
        cities = [
            "مراكش", "الرباط", "الدار البيضاء", "فاس", "طنجة", "أكادير",
            "باريس", "لندن", "مدريد", "روما", "دبي", "القاهرة", "نيويورك", "اسطنبول"
        ]
        
        for city in cities:
            if city in message:
                return city
        return message
    
    def _extract_trip_type(self, message: str) -> str:
        if 'إياب' in message or 'ذهاب وإياب' in message:
            return "ذهاب وإياب"
        elif 'ذهاب فقط' in message or 'فقط' in message:
            return "ذهاب فقط"
        return "ذهاب وإياب"
    
    def _extract_flight_class(self, message: str) -> str:
        if 'اقتصادية' in message:
            return "اقتصادية"
        elif 'رجال أعمال' in message or 'أعمال' in message:
            return "رجال أعمال"
        elif 'أولى' in message or 'درجة أولى' in message:
            return "درجة أولى"
        return "اقتصادية"
    
    def _extract_hotel_category(self, message: str) -> str:
        if '5 نجوم' in message or '5' in message:
            return "5 نجوم"
        elif '4 نجوم' in message or '4' in message:
            return "4 نجوم"
        elif '3 نجوم' in message or '3' in message:
            return "3 نجوم"
        return "4 نجوم"
    
    def _extract_number_of_people(self, message: str) -> str:
        if 'شخص واحد' in message or 'واحد' in message or '1' in message:
            return "شخص واحد"
        elif 'شخصين' in message or 'شخصان' in message or '2' in message:
            return "شخصين"
        elif '3 أشخاص' in message or 'ثلاثة' in message or '3' in message:
            return "3 أشخاص"
        elif '4 أشخاص' in message or 'أربعة' in message or '4' in message:
            return "4 أشخاص"
        return message
    
    def _extract_hotel_district(self, message: str) -> str:
        if 'وسط المدينة' in message or 'وسط' in message:
            return "وسط المدينة"
        elif 'المدينة القديمة' in message or 'القديمة' in message:
            return "المدينة القديمة"
        elif 'المطار' in message:
            return "قريب من المطار"
        elif 'السياحية' in message or 'سياحية' in message:
            return "المنطقة السياحية"
        return message

class ActionSelectOption(Action):
    def name(self) -> Text:
        return "action_select_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Redirect to process user input to handle option selection properly
        return [FollowupAction("action_process_user_input")]

class ActionConfirmReservation(Action):
    def name(self) -> Text:
        return "action_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        
        if sender_id in conversations and 'booking_summary' in conversations[sender_id]:
            conv_data = conversations[sender_id]
            booking_data = conv_data['booking_summary']
            booking_type = conv_data.get('booking_type', 'flight')
            
            if booking_type == 'hotel':
                # Hotel confirmation
                response = f"✅ تم تأكيد حجز إقامتك في {booking_data['name']}!\n\n"
                response += f"📝 تفاصيل الحجز:\n"
                response += f"• اسم الفندق: {booking_data['name']}\n"
                response += f"• الفئة: {booking_data['category']}\n"
                response += f"• الموقع: {booking_data['district']} - {booking_data['city']}\n"
                response += f"• عدد الأشخاص: {conv_data.get('number_of_people', 'غير محدد')}\n"
                response += f"• السعر: {booking_data['price']}\n"
                response += f"• الخدمات: {booking_data['amenities']}\n"
                response += f"• التقييم: {booking_data['rating']}\n\n"
                response += "🙏 شكراً لثقتك بنا. نتمنى لك إقامة سعيدة ومريحة! 🏨"
            else:
                # Flight confirmation
                response = f"✅ تم تأكيد حجز رحلتك مع {booking_data['airline']}!\n\n"
                response += f"📝 تفاصيل الحجز:\n"
                response += f"• رقم الرحلة: {booking_data['flight_number']}\n"
                response += f"• من {booking_data['departure']} إلى {booking_data['destination']}\n"
                response += f"• التاريخ: {booking_data['date']}\n"
                response += f"• وقت المغادرة: {booking_data['departure_time']}\n"
                response += f"• الدرجة: {booking_data['class']}\n"
                response += f"• السعر: {booking_data['price']}\n\n"
                response += "🙏 شكراً لثقتك بنا. نتمنى لك رحلة سعيدة وآمنة! ✈️"
            
            # Clear conversation data
            conversations[sender_id] = {}
        else:
            response = "✅ تم تأكيد حجزك بنجاح! 🙏 شكراً لثقتك بنا."
        
        dispatcher.utter_message(text=response)
        return []

class ActionUpdateBooking(Action):
    def name(self) -> Text:
        return "action_update_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sender_id = tracker.sender_id
        print(f"DEBUG - ActionUpdateBooking for sender: {sender_id}")
        
        if sender_id in conversations:
            conv_data = conversations[sender_id]
            booking_type = conv_data.get('booking_type', 'flight')
            
            print(f"DEBUG - Booking type: {booking_type}")
            print(f"DEBUG - Clearing all data for fresh start")
            
            # COMPLETELY CLEAR ALL COLLECTED DATA
            keys_to_clear = [
                'departure_city', 'destination_city', 'departure_date', 
                'trip_type', 'flight_class', 'booking_summary', 
                'available_flights', 'available_hotels', 'next_question',
                'hotel_city', 'hotel_category', 'number_of_people', 'hotel_district'
            ]
            
            for key in keys_to_clear:
                if key in conv_data:
                    del conv_data[key]
                    print(f"DEBUG - Cleared {key}")
            
            # Start fresh based on booking type
            if booking_type == 'hotel':
                dispatcher.utter_message(text="سأساعدك في البحث عن فندق جديد. دعنا نبدأ من البداية.")
                conv_data['next_question'] = 'hotel_city'
                conv_data['booking_type'] = 'hotel'
                return [FollowupAction("action_search_hotel")]
            else:
                dispatcher.utter_message(text="سأساعدك في البحث عن رحلة جديدة. دعنا نبدأ من البداية.")
                conv_data['next_question'] = 'departure_city'
                conv_data['booking_type'] = 'flight'
                return [FollowupAction("action_search_flight")]
        else:
            # No existing conversation
            dispatcher.utter_message(text="لا يوجد حجز حالي للتعديل. يمكنك بدء حجز جديد بقول 'أريد حجز رحلة' أو 'أريد حجز فندق'.")
            return []