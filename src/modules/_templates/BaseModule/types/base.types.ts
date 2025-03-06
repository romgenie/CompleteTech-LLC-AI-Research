/**
 * Base types for module components
 */

// Base entity interface - will be extended by specific entities
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

// Base filter type - will be extended by specific filters
export interface BaseFilter {
  search?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

// Base pagination response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Base module display modes
export type ModuleDisplayMode = 'list' | 'grid' | 'detail' | 'form';

// Base module props
export interface BaseModuleProps<T extends BaseEntity, F extends BaseFilter> {
  mode?: ModuleDisplayMode;
  initialFilter?: Partial<F>;
  onItemSelect?: (item: T) => void;
  onItemCreate?: (item: T) => void;
  onItemUpdate?: (item: T) => void;
  onItemDelete?: (id: string) => void;
  readOnly?: boolean;
  height?: string | number;
  width?: string | number;
  showActions?: boolean;
  showFilters?: boolean;
  customActions?: React.ReactNode;
  filterComponent?: React.ComponentType<BaseFilterProps<F>>;
  listComponent?: React.ComponentType<BaseListProps<T, F>>;
  cardComponent?: React.ComponentType<BaseCardProps<T>>;
  detailComponent?: React.ComponentType<BaseDetailProps<T>>;
  formComponent?: React.ComponentType<BaseFormProps<T>>;
  emptyComponent?: React.ComponentType<BaseEmptyProps>;
  errorComponent?: React.ComponentType<BaseErrorProps>;
  loadingComponent?: React.ComponentType<BaseLoadingProps>;
}

// Component prop interfaces
export interface BaseFilterProps<F extends BaseFilter> {
  filter: F;
  onFilterChange: (filter: F) => void;
}

export interface BaseListProps<T extends BaseEntity, F extends BaseFilter> {
  items: T[];
  filter: F;
  loading: boolean;
  error: Error | null;
  onFilterChange: (filter: F) => void;
  onItemSelect?: (item: T) => void;
  onItemDelete?: (id: string) => void;
  readOnly?: boolean;
}

export interface BaseCardProps<T extends BaseEntity> {
  item: T;
  onSelect?: (item: T) => void;
  onDelete?: (id: string) => void;
  readOnly?: boolean;
}

export interface BaseDetailProps<T extends BaseEntity> {
  item: T;
  loading: boolean;
  error: Error | null;
  onEdit?: (item: T) => void;
  onDelete?: (id: string) => void;
  readOnly?: boolean;
}

export interface BaseFormProps<T extends BaseEntity> {
  item?: T;
  onSubmit: (data: Partial<T>) => void;
  onCancel?: () => void;
  loading?: boolean;
  error?: Error | null;
}

export interface BaseEmptyProps {
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export interface BaseErrorProps {
  error: Error | null;
  onRetry?: () => void;
}

export interface BaseLoadingProps {
  message?: string;
}
