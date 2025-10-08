export interface Schedule {
  id: number;
  name: string;
  cron_expression: string;
  target_channel_ids: number[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  next_run?: string;
}

export interface ScheduleCreateInput {
  name: string;
  cron_expression: string;
  target_channel_ids: number[];
  is_active: boolean;
}

export interface ScheduleUpdateInput {
  name?: string;
  cron_expression?: string;
  target_channel_ids?: number[];
  is_active?: boolean;
}
