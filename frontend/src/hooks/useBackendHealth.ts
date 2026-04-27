import { useCallback, useState } from 'react';
import api from '../services/api';
import { getHealthStatusText } from '../utils/health';

type UseBackendHealthState = {
  loading: boolean;
  statusText: string;
  isError: boolean;
};

export const useBackendHealth = (): UseBackendHealthState & {
  checkHealth: () => Promise<void>;
} => {
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('Checking...');
  const [isError, setIsError] = useState(false);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setIsError(false);

    try {
      const response = await api.getHealth();
      if (response.success && response.data) {
        setStatusText(getHealthStatusText(response.data.status, false));
      } else {
        setIsError(true);
        setStatusText(getHealthStatusText(response.error, true));
      }
    } catch (error) {
      const fallback = error instanceof Error ? error.message : 'Unknown backend error';
      setIsError(true);
      setStatusText(getHealthStatusText(fallback, true));
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, statusText, isError, checkHealth };
};
