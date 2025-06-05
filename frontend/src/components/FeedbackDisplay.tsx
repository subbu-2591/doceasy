import React from 'react';
import { Star, StarOff } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";

interface FeedbackDisplayProps {
  feedback: {
    rating: number;
    feedback: string;
    doctorName: string;
    timestamp: string;
  };
}

const FeedbackDisplay = ({ feedback }: FeedbackDisplayProps) => {
  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="space-y-2">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium">Dr. {feedback.doctorName}</h4>
              <p className="text-sm text-gray-500">{formatDate(feedback.timestamp)}</p>
            </div>
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <span key={star}>
                  {star <= feedback.rating ? (
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  ) : (
                    <StarOff className="w-4 h-4 text-gray-300" />
                  )}
                </span>
              ))}
            </div>
          </div>
          <p className="text-gray-600">{feedback.feedback}</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default FeedbackDisplay; 