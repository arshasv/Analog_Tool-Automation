export const getHealthStatusText = (value: string | undefined, isError: boolean): string => {
  if (isError) {
    return `Error ❌ ${value ?? 'Backend unreachable'}`;
  }

  const normalized = value?.trim().toLowerCase();
  if (normalized === 'ok' || normalized === 'healthy') {
    return 'Online';
  }

  return `Online (${value ?? 'unknown status'})`;
};
