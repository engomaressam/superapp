<![CDATA[/**
 * ActionCard Component
 * 
 * Displays pending actions that require user confirmation.
 * Shows action details and confirm/cancel buttons.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';

const COLORS = {
  primary: '#6366f1',
  background: '#0f172a',
  surface: '#1e293b',
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
};

interface ActionDetails {
  id: string;
  type: string;
  status: string;
  details: Record<string, any>;
}

interface ActionCardProps {
  action: ActionDetails;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ActionCard({ action, onConfirm, onCancel }: ActionCardProps) {
  const getIcon = () => {
    switch (action.type) {
      case 'ride_booking':
        return 'car';
      case 'appointment':
        return 'medical';
      case 'calendar_event':
        return 'calendar';
      case 'reminder':
        return 'alarm';
      default:
        return 'checkmark-circle';
    }
  };

  const getTitle = () => {
    switch (action.type) {
      case 'ride_booking':
        return 'Book Ride';
      case 'appointment':
        return 'Book Appointment';
      case 'calendar_event':
        return 'Create Event';
      case 'reminder':
        return 'Set Reminder';
      default:
        return 'Confirm Action';
    }
  };

  const renderDetails = () => {
    const details = action.details || {};

    switch (action.type) {
      case 'ride_booking':
        return (
          <>
            <DetailRow icon="location" label="To" value={details.destination || 'Destination'} />
            <DetailRow icon="car" label="Type" value={details.ride_type || 'UberX'} />
            <DetailRow icon="cash" label="Price" value={`$${details.estimated_price || '?'}`} />
            <DetailRow icon="time" label="ETA" value={`${details.eta || '?'} minutes`} />
          </>
        );

      case 'appointment':
        return (
          <>
            <DetailRow icon="person" label="Doctor" value={details.doctor || 'Doctor'} />
            <DetailRow icon="time" label="Time" value={details.time || 'TBD'} />
            <DetailRow icon="location" label="Location" value={details.location || 'Clinic'} />
            <DetailRow icon="cash" label="Fee" value={`${details.fee || '?'} EGP`} />
          </>
        );

      default:
        return Object.entries(details).map(([key, value]) => (
          <DetailRow
            key={key}
            icon="information-circle"
            label={key.replace(/_/g, ' ')}
            value={String(value)}
          />
        ));
    }
  };

  return (
    <Animated.View style={styles.container}>
      <BlurView intensity={20} style={styles.blur}>
        <View style={styles.card}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.iconContainer}>
              <Ionicons name={getIcon() as any} size={24} color={COLORS.primary} />
            </View>
            <View style={styles.headerText}>
              <Text style={styles.title}>{getTitle()}</Text>
              <Text style={styles.subtitle}>Requires confirmation</Text>
            </View>
          </View>

          {/* Details */}
          <View style={styles.details}>
            {renderDetails()}
          </View>

          {/* Actions */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onCancel}
            >
              <Ionicons name="close" size={20} color={COLORS.error} />
              <Text style={[styles.buttonText, styles.cancelText]}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.confirmButton]}
              onPress={onConfirm}
            >
              <Ionicons name="checkmark" size={20} color={COLORS.text} />
              <Text style={[styles.buttonText, styles.confirmText]}>Confirm</Text>
            </TouchableOpacity>
          </View>
        </View>
      </BlurView>
    </Animated.View>
  );
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.detailRow}>
      <View style={styles.detailLabel}>
        <Ionicons name={icon as any} size={16} color={COLORS.textSecondary} />
        <Text style={styles.labelText}>{label}</Text>
      </View>
      <Text style={styles.valueText}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 100,
    left: 10,
    right: 10,
  },
  blur: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  card: {
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(99, 102, 241, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerText: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
  },
  subtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  details: {
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  detailLabel: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  labelText: {
    color: COLORS.textSecondary,
    fontSize: 14,
    marginLeft: 8,
    textTransform: 'capitalize',
  },
  valueText: {
    color: COLORS.text,
    fontSize: 14,
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  cancelButton: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  confirmButton: {
    backgroundColor: COLORS.primary,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  cancelText: {
    color: COLORS.error,
  },
  confirmText: {
    color: COLORS.text,
  },
});
]]>
