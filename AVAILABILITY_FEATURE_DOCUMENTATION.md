# Doctor Weekly Availability Management Feature

## Overview

This feature allows doctors to manage their weekly availability schedule through the doctor dashboard. Patients can then view this availability when booking appointments, ensuring appointments are only scheduled during the doctor's available time slots.

## Features Implemented

### 1. Backend Implementation

#### Database Model (`DoctorAvailability`)
- **Collection**: `doctor_availability`
- **Structure**:
  ```json
  {
    "_id": "ObjectId",
    "doctor_id": "string",
    "weekly_availability": {
      "monday": {
        "is_available": false,
        "time_slots": []
      },
      "tuesday": {
        "is_available": true,
        "time_slots": [
          {
            "start_time": "09:00",
            "end_time": "12:00"
          },
          {
            "start_time": "14:00",
            "end_time": "17:00"
          }
        ]
      },
      // ... other days
    },
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

#### API Endpoints

##### Doctor Endpoints (Authenticated)
- `GET /api/doctor/availability` - Get doctor's weekly availability
- `PUT /api/doctor/availability` - Update doctor's weekly availability
- `GET /api/doctor/availability/day/<day_of_week>` - Get availability for specific day

##### Public Endpoints (For Patient Booking)
- `GET /api/doctors/<doctor_id>/availability` - Get doctor's availability (public)
- `GET /api/doctors/<doctor_id>/availability/date/<date>` - Get available slots for specific date

#### Model Methods
- `create_default_availability()` - Creates default weekly structure
- `create_or_update()` - Upsert availability data
- `find_by_doctor_id()` - Get availability by doctor ID
- `get_available_slots_for_day()` - Get time slots for specific day
- `is_doctor_available()` - Check if doctor is available at specific datetime

### 2. Frontend Implementation

#### New Tab in Doctor Dashboard
- Added "Weekly Availability" tab to the doctor dashboard
- Comprehensive UI for managing weekly schedules
- Real-time updates and validation

#### UI Components
- **Day Toggle**: Switch to enable/disable availability for each day
- **Time Slot Management**: Add, edit, and remove time slots
- **Visual Feedback**: Loading states, success/error messages
- **Responsive Design**: Works on desktop and mobile devices

#### Features
- **Add Time Slots**: Doctors can add multiple time slots per day
- **Edit Time Slots**: Modify start and end times with time pickers
- **Remove Time Slots**: Delete unwanted time slots
- **Save Changes**: Persist changes to the database
- **Real-time Validation**: Prevent overlapping time slots
- **Help Tips**: Guidance for setting up availability

### 3. User Interface

#### Doctor Dashboard - Availability Tab
```
┌─────────────────────────────────────────────────────────┐
│ Weekly Availability                    [Save Changes]   │
├─────────────────────────────────────────────────────────┤
│ Monday                                Available [Toggle] │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Time Slots                          [Add Slot]     │ │
│ │ From: 09:00  To: 12:00                    [Delete] │ │
│ │ From: 14:00  To: 17:00                    [Delete] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Tuesday                               Available [Toggle] │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ No time slots configured for this day               │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ... (other days)                                        │
└─────────────────────────────────────────────────────────┘
```

## Usage Instructions

### For Doctors

1. **Access Availability Management**:
   - Log in to the doctor dashboard
   - Navigate to the "Weekly Availability" tab

2. **Set Daily Availability**:
   - Toggle the "Available" switch for each day you want to work
   - Days are disabled by default

3. **Add Time Slots**:
   - Click "Add Slot" for available days
   - Set start and end times using the time pickers
   - Add multiple slots for different sessions (e.g., morning/evening)

4. **Edit Time Slots**:
   - Modify start/end times directly in the time inputs
   - Changes are tracked automatically

5. **Remove Time Slots**:
   - Click the delete button (trash icon) next to unwanted slots

6. **Save Changes**:
   - Click "Save Changes" to persist your availability
   - Success/error messages will confirm the operation

### For Patients (Future Integration)

1. **View Doctor Availability**:
   - When booking appointments, patients will see available time slots
   - Only slots within the doctor's availability will be shown

2. **Book Appointments**:
   - Select from available time slots
   - System prevents booking outside available hours

## Technical Implementation Details

### Backend Architecture

#### Models Integration
```python
# Import in routes.py
from models import DoctorAvailability

# Usage in endpoints
availability = DoctorAvailability.find_by_doctor_id(db, doctor_id)
```

#### Error Handling
- Comprehensive try-catch blocks
- Proper HTTP status codes
- Detailed error messages
- Logging for debugging

#### Data Validation
- Required field validation
- Time format validation
- Doctor authentication checks
- Data structure validation

### Frontend Architecture

#### State Management
```typescript
interface AvailabilityData {
  id?: string;
  doctor_id: string;
  weekly_availability: WeeklyAvailability;
  created_at?: string;
  updated_at?: string;
}
```

#### API Integration
- Axios for HTTP requests
- JWT token authentication
- Error handling with toast notifications
- Loading states for better UX

#### Component Structure
- Modular design with reusable components
- TypeScript interfaces for type safety
- Responsive design with Tailwind CSS
- Accessibility considerations

## Security Considerations

### Authentication
- JWT token required for all doctor endpoints
- Role-based access control (doctor role required)
- Token validation on every request

### Authorization
- Doctors can only modify their own availability
- Public endpoints only show approved doctors
- Input validation and sanitization

### Data Protection
- Sensitive data excluded from responses
- Proper error handling without data leakage
- CORS configuration maintained

## Testing

### Backend Testing
- Model import verification
- Default availability structure creation
- Route registration confirmation
- Database operations testing

### Frontend Testing
- Component rendering tests
- State management verification
- API integration testing
- User interaction testing

## Future Enhancements

### Planned Features
1. **Recurring Availability**: Set patterns that repeat weekly
2. **Holiday Management**: Mark specific dates as unavailable
3. **Appointment Buffer**: Add time between appointments
4. **Bulk Operations**: Copy availability between days
5. **Template System**: Save and reuse availability templates

### Integration Opportunities
1. **Calendar Sync**: Integration with Google Calendar, Outlook
2. **Notification System**: Alerts for availability changes
3. **Analytics**: Track availability utilization
4. **Mobile App**: Native mobile availability management

## Deployment Notes

### Database Migration
- No migration required (new collection will be created automatically)
- Existing data remains unchanged
- Default availability created on first access

### Environment Setup
- No additional environment variables required
- Uses existing MongoDB connection
- Compatible with current authentication system

### Monitoring
- Monitor new API endpoints for performance
- Track availability update frequency
- Monitor patient booking patterns

## Troubleshooting

### Common Issues

1. **Availability Not Saving**:
   - Check JWT token validity
   - Verify doctor authentication
   - Check network connectivity
   - Review browser console for errors

2. **Time Slots Not Displaying**:
   - Ensure day is marked as available
   - Check time format (HH:MM)
   - Verify data structure in database

3. **UI Not Loading**:
   - Check component imports
   - Verify API endpoint availability
   - Review browser console for JavaScript errors

### Debug Information
- Enable debug mode in Flask for detailed error messages
- Check browser network tab for API request/response details
- Review server logs for backend errors
- Use React Developer Tools for component state inspection

## API Documentation

### Request/Response Examples

#### Get Availability
```http
GET /api/doctor/availability
Authorization: Bearer <jwt_token>

Response:
{
  "availability": {
    "id": "...",
    "doctor_id": "...",
    "weekly_availability": { ... }
  },
  "doctorId": "..."
}
```

#### Update Availability
```http
PUT /api/doctor/availability
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "weekly_availability": {
    "monday": {
      "is_available": true,
      "time_slots": [
        {
          "start_time": "09:00",
          "end_time": "12:00"
        }
      ]
    },
    // ... other days
  }
}

Response:
{
  "message": "Availability updated successfully",
  "availability": { ... }
}
```

## Conclusion

The Doctor Weekly Availability Management feature provides a comprehensive solution for doctors to manage their schedules and for patients to book appointments during available times. The implementation follows best practices for security, usability, and maintainability, making it a robust addition to the DocEasy platform.

The feature is production-ready and can be deployed immediately. Future enhancements can be added incrementally without affecting the core functionality. 