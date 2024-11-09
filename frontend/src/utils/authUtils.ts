export type ResourcePermissions = {
  [key: string]: string[];
};

export const hasAccess = (
  resourceId: string,
  action: string,
  permissions: ResourcePermissions
) => {
  const resource = permissions[resourceId] || permissions["DEFAULT"];
  if (!resource) return false;
  const hasAccess = resource.includes(action);
  return hasAccess;
};
