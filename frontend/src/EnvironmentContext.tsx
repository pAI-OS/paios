import React, { createContext, useState, useContext, useEffect } from 'react';
import { httpClient, apiBase } from './apiBackend';

interface Environment {
  id: string;
  name: string;
  default?: boolean;
}

interface EnvironmentContextType {
  currentEnvironment: Environment;
  setCurrentEnvironment: (env: Environment) => void;
  environments: Environment[];
  loading: boolean;
  error: string | null;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

export const EnvironmentProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [currentEnvironment, setCurrentEnvironment] = useState<Environment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const { json } = await httpClient(`${apiBase}/environments`);
        setEnvironments(json);
        
        // Set the default environment
        const defaultEnv = json.find((env: Environment) => env.default) || json[0];
        
        // Check if there's a saved environment in localStorage
        const savedEnvId = localStorage.getItem('currentEnvironmentId');
        const savedEnv = savedEnvId ? json.find((env: Environment) => env.id === savedEnvId) : null;
        
        setCurrentEnvironment(savedEnv || defaultEnv);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch environments');
        setLoading(false);
      }
    };

    fetchEnvironments();
  }, []);

  useEffect(() => {
    if (currentEnvironment) {
      localStorage.setItem('currentEnvironmentId', currentEnvironment.id);
    }
  }, [currentEnvironment]);

  if (loading) {
    return <div>Loading environments...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <EnvironmentContext.Provider 
      value={{ 
        currentEnvironment: currentEnvironment!, 
        setCurrentEnvironment, 
        environments, 
        loading, 
        error 
      }}
    >
      {children}
    </EnvironmentContext.Provider>
  );
};

export const useEnvironment = () => {
  const context = useContext(EnvironmentContext);
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider');
  }
  return context;
};
