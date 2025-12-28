<![CDATA[/**
 * useARIA Hook
 * 
 * Main hook for interacting with the ARIA backend.
 * Handles API calls, state management, and real-time updates.
 */

import { useState, useCallback } from 'react';
import * as Location from 'expo-location';
import { api, ChatResponse, ActionConfirmResponse } from '../services/api';

interface UseARIAReturn {
  sendMessage: (message: string) => Promise<ChatResponse>;
  confirmAction: (actionId: string, confirmed: boolean) => Promise<ActionConfirmResponse>;
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
}

export function useARIA(): UseARIAReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  /**
   * Send a message to ARIA and get a response.
   */
  const sendMessage = useCallback(async (message: string): Promise<ChatResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      // Get user location for context
      let location = null;
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const loc = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Balanced,
          });
          location = {
            lat: loc.coords.latitude,
            lng: loc.coords.longitude,
          };
        }
      } catch (locError) {
        console.log('Location not available:', locError);
      }

      // Send message to API
      const response = await api.sendMessage({
        message,
        conversation_id: conversationId || undefined,
        context: {
          location,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        },
      });

      // Update conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to send message';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  /**
   * Confirm or reject a pending action.
   */
  const confirmAction = useCallback(async (
    actionId: string,
    confirmed: boolean
  ): Promise<ActionConfirmResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.confirmAction(actionId, {
        confirmed,
      });
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to confirm action';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    sendMessage,
    confirmAction,
    isLoading,
    error,
    conversationId,
  };
}
]]>
