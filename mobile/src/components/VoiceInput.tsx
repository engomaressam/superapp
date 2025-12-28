<![CDATA[/**
 * VoiceInput Component
 * 
 * Floating button for voice input with speech-to-text.
 */

import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Text,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
// Note: expo-speech-recognition would be needed for actual implementation

const COLORS = {
  primary: '#6366f1',
  surface: '#1e293b',
  text: '#f8fafc',
  accent: '#22d3ee',
};

interface VoiceInputProps {
  onTranscript: (text: string) => void;
}

export function VoiceInput({ onTranscript }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [pulseAnim] = useState(new Animated.Value(1));

  const startPulse = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopPulse = () => {
    pulseAnim.setValue(1);
  };

  const handlePress = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    if (isListening) {
      // Stop listening
      setIsListening(false);
      stopPulse();
      
      // In production, this would stop the speech recognition
      // and return the transcript
      // For demo, we'll simulate a response
      setTimeout(() => {
        onTranscript("Book me an Uber to Cairo Festival City");
      }, 500);
    } else {
      // Start listening
      setIsListening(true);
      startPulse();
      
      // In production, this would start speech recognition
      // using expo-speech-recognition or a similar package
    }
  };

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.pulseRing,
          {
            transform: [{ scale: pulseAnim }],
            opacity: isListening ? 0.3 : 0,
          },
        ]}
      />
      <TouchableOpacity
        style={[
          styles.button,
          isListening && styles.buttonActive,
        ]}
        onPress={handlePress}
        onLongPress={handlePress}
      >
        <Ionicons
          name={isListening ? 'mic' : 'mic-outline'}
          size={28}
          color={isListening ? COLORS.text : COLORS.primary}
        />
      </TouchableOpacity>
      
      {isListening && (
        <View style={styles.listeningIndicator}>
          <Text style={styles.listeningText}>Listening...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 100,
    right: 20,
    alignItems: 'center',
  },
  pulseRing: {
    position: 'absolute',
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: COLORS.primary,
  },
  button: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: COLORS.surface,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    borderWidth: 2,
    borderColor: COLORS.primary,
  },
  buttonActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.accent,
  },
  listeningIndicator: {
    position: 'absolute',
    bottom: 70,
    backgroundColor: COLORS.surface,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  listeningText: {
    color: COLORS.accent,
    fontSize: 12,
    fontWeight: '600',
  },
});
]]>
