 import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../constants/Colors';
import { Biomarker } from '../constants/Types';

interface BiomarkerDisplayProps {
  name: string;
  biomarker: Biomarker;
}

export default function BiomarkerDisplay({ name, biomarker }: BiomarkerDisplayProps) {
  const getStatusIcon = () => {
    switch (biomarker.status) {
      case 'normal':
        return <Ionicons name="checkmark-circle" size={20} color={Colors.light.success} />;
      case 'borderline':
        return <Ionicons name="alert-circle" size={20} color={Colors.light.warning} />;
      case 'abnormal':
        return <Ionicons name="warning" size={20} color={Colors.light.error} />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (biomarker.status) {
      case 'normal':
        return Colors.light.success;
      case 'borderline':
        return Colors.light.warning;
      case 'abnormal':
        return Colors.light.error;
      default:
        return Colors.light.text;
    }
  };

  const formatName = (name: string) => {
    return name
      .split(/(?=[A-Z])/)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.name}>{formatName(name)}</Text>
        {getStatusIcon()}
      </View>
      
      <View style={styles.valueContainer}>
        <Text style={styles.value}>
          {biomarker.value} <Text style={styles.unit}>{biomarker.unit}</Text>
        </Text>
      </View>
      
      <View style={styles.rangeContainer}>
        <Text style={styles.rangeLabel}>Normal Range:</Text>
        <Text style={styles.rangeValue}>{biomarker.range}</Text>
      </View>
      
      <View style={[styles.statusBadge, { backgroundColor: getStatusColor() + '20' }]}>
        <Text style={[styles.statusText, { color: getStatusColor() }]}>
          {biomarker.status.toUpperCase()}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.light.text,
  },
  valueContainer: {
    marginBottom: 8,
  },
  value: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.light.text,
  },
  unit: {
    fontSize: 16,
    fontWeight: '400',
    color: '#6B7280',
  },
  rangeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  rangeLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginRight: 8,
  },
  rangeValue: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.light.text,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
