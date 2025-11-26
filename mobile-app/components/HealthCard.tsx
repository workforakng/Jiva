import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../constants/Colors';
import { HealthRecord } from '../constants/Types';

interface HealthCardProps {
  record: HealthRecord;
  onPress: () => void;
}

export default function HealthCard({ record, onPress }: HealthCardProps) {
  const getIconName = (type: string) => {
    switch (type.toLowerCase()) {
      case 'blood test':
        return 'water';
      case 'lipid panel':
        return 'heart';
      case 'complete blood count':
        return 'medical';
      case 'liver function test':
        return 'fitness';
      default:
        return 'document-text';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getBiomarkerCount = () => {
    return Object.keys(record.biomarkers).length;
  };

  const getStatusColor = () => {
    const statuses = Object.values(record.biomarkers).map((b) => b.status);
    if (statuses.includes('abnormal')) return Colors.light.error;
    if (statuses.includes('borderline')) return Colors.light.warning;
    return Colors.light.success;
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.iconContainer}>
        <Ionicons name={getIconName(record.type) as any} size={24} color={Colors.light.primary} />
      </View>
      
      <View style={styles.content}>
        <Text style={styles.title}>{record.type}</Text>
        <Text style={styles.facility}>{record.facility}</Text>
        <Text style={styles.date}>{formatDate(record.date)}</Text>
        
        <View style={styles.footer}>
          <View style={styles.biomarkerBadge}>
            <Text style={styles.biomarkerText}>{getBiomarkerCount()} biomarkers</Text>
          </View>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.light.text,
    marginBottom: 4,
  },
  facility: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  biomarkerBadge: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  biomarkerText: {
    fontSize: 11,
    color: '#6B7280',
    fontWeight: '500',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});
