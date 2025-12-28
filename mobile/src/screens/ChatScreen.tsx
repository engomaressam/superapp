<![CDATA[/**
 * ChatScreen - Main conversation interface
 * 
 * This is the primary screen where users interact with ARIA.
 * Features:
 * - Natural language chat input
 * - Voice input support
 * - Action cards for confirmations
 * - Real-time status updates
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { GiftedChat, IMessage, Bubble, Send, InputToolbar } from 'react-native-gifted-chat';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';

import { useARIA } from '../hooks/useARIA';
import { ActionCard } from '../components/ActionCard';
import { VoiceInput } from '../components/VoiceInput';
import { TypingIndicator } from '../components/TypingIndicator';

// Theme colors
const COLORS = {
  primary: '#6366f1',
  background: '#0f172a',
  surface: '#1e293b',
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  accent: '#22d3ee',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
};

export default function ChatScreen() {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [pendingAction, setPendingAction] = useState<any>(null);
  
  const { sendMessage, confirmAction, isLoading } = useARIA();

  // Welcome message on mount
  useEffect(() => {
    setMessages([
      {
        _id: 'welcome',
        text: "Hello! I'm ARIA, your personal AI assistant. I can help you book rides, schedule appointments, check your calendar, and much more. What would you like to do today?",
        createdAt: new Date(),
        user: {
          _id: 'aria',
          name: 'ARIA',
          avatar: require('../assets/aria-avatar.png'),
        },
      },
    ]);
  }, []);

  // Handle sending messages
  const onSend = useCallback(async (newMessages: IMessage[] = []) => {
    const userMessage = newMessages[0];
    
    // Add user message immediately
    setMessages(previousMessages =>
      GiftedChat.append(previousMessages, newMessages)
    );
    
    // Haptic feedback
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    // Show typing indicator
    setIsTyping(true);
    
    try {
      // Send to backend
      const response = await sendMessage(userMessage.text);
      
      // Process response
      const ariaMessage: IMessage = {
        _id: response.response_id,
        text: response.message,
        createdAt: new Date(),
        user: {
          _id: 'aria',
          name: 'ARIA',
          avatar: require('../assets/aria-avatar.png'),
        },
      };
      
      setMessages(previousMessages =>
        GiftedChat.append(previousMessages, [ariaMessage])
      );
      
      // Handle actions if any
      if (response.actions && response.actions.length > 0) {
        setPendingAction(response.actions[0]);
      }
      
      // Haptic feedback for response
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: IMessage = {
        _id: `error-${Date.now()}`,
        text: "Sorry, I encountered an issue processing your request. Please try again.",
        createdAt: new Date(),
        user: {
          _id: 'aria',
          name: 'ARIA',
        },
      };
      
      setMessages(previousMessages =>
        GiftedChat.append(previousMessages, [errorMessage])
      );
      
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setIsTyping(false);
    }
  }, [sendMessage]);

  // Handle action confirmation
  const handleActionConfirm = async (confirmed: boolean) => {
    if (!pendingAction) return;
    
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    try {
      const result = await confirmAction(pendingAction.id, confirmed);
      
      const responseMessage: IMessage = {
        _id: `action-${Date.now()}`,
        text: confirmed
          ? `✅ Done! ${result.result?.message || 'Action completed successfully.'}`
          : '❌ Action cancelled.',
        createdAt: new Date(),
        user: {
          _id: 'aria',
          name: 'ARIA',
        },
      };
      
      setMessages(previousMessages =>
        GiftedChat.append(previousMessages, [responseMessage])
      );
      
    } catch (error) {
      Alert.alert('Error', 'Failed to process action. Please try again.');
    } finally {
      setPendingAction(null);
    }
  };

  // Handle voice input
  const handleVoiceInput = (transcript: string) => {
    if (transcript) {
      onSend([{
        _id: `voice-${Date.now()}`,
        text: transcript,
        createdAt: new Date(),
        user: { _id: 'user' },
      }]);
    }
  };

  // Custom bubble styling
  const renderBubble = (props: any) => (
    <Bubble
      {...props}
      wrapperStyle={{
        right: {
          backgroundColor: COLORS.primary,
        },
        left: {
          backgroundColor: COLORS.surface,
        },
      }}
      textStyle={{
        right: {
          color: COLORS.text,
        },
        left: {
          color: COLORS.text,
        },
      }}
    />
  );

  // Custom send button
  const renderSend = (props: any) => (
    <Send {...props} containerStyle={styles.sendContainer}>
      <View style={styles.sendButton}>
        <Ionicons name="send" size={20} color={COLORS.text} />
      </View>
    </Send>
  );

  // Custom input toolbar
  const renderInputToolbar = (props: any) => (
    <InputToolbar
      {...props}
      containerStyle={styles.inputToolbar}
      primaryStyle={styles.inputPrimary}
    />
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <GiftedChat
        messages={messages}
        onSend={onSend}
        user={{ _id: 'user' }}
        renderBubble={renderBubble}
        renderSend={renderSend}
        renderInputToolbar={renderInputToolbar}
        isTyping={isTyping}
        renderFooter={() => isTyping ? <TypingIndicator /> : null}
        placeholder="Message ARIA..."
        alwaysShowSend
        scrollToBottom
        inverted
      />
      
      {/* Voice Input Button */}
      <VoiceInput onTranscript={handleVoiceInput} />
      
      {/* Action Confirmation Card */}
      {pendingAction && (
        <ActionCard
          action={pendingAction}
          onConfirm={() => handleActionConfirm(true)}
          onCancel={() => handleActionConfirm(false)}
        />
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  sendContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    marginBottom: 5,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inputToolbar: {
    backgroundColor: COLORS.surface,
    borderTopWidth: 0,
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginHorizontal: 10,
    marginBottom: 10,
    borderRadius: 25,
  },
  inputPrimary: {
    alignItems: 'center',
  },
});
]]>
