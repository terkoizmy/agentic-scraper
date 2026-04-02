import { useState, useEffect, useCallback } from 'react';
import { getAgentSettings, patchAgentSettings } from '@/lib/api';

interface AgentSettings {
  thinkingEnabled: boolean;
  thinkingMaxTokens: number;
}

export function useAgentSettings() {
  const [settings, setSettings] = useState<AgentSettings>({
    thinkingEnabled: false,
    thinkingMaxTokens: 1024,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAgentSettings()
      .then((data) => {
        setSettings({
          thinkingEnabled: data.thinking_enabled,
          thinkingMaxTokens: data.thinking_max_tokens,
        });
      })
      .catch((err) => {
        console.error('Failed to load agent settings:', err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const updateSettings = useCallback(async (patch: Partial<AgentSettings>) => {
    const apiPatch: Partial<{ thinking_enabled: boolean; thinking_max_tokens: number }> = {};
    if (patch.thinkingEnabled !== undefined) {
      apiPatch.thinking_enabled = patch.thinkingEnabled;
    }
    if (patch.thinkingMaxTokens !== undefined) {
      apiPatch.thinking_max_tokens = patch.thinkingMaxTokens;
    }

    await patchAgentSettings(apiPatch);
    setSettings((prev) => ({ ...prev, ...patch }));
  }, []);

  return { settings, loading, updateSettings };
}