-- ==============================================================================
-- NEXUS AI STARTUP VALIDATOR - SUPABASE DATABASE SCHEMA
-- ==============================================================================
-- HOW TO USE:
-- 1. Open your Supabase Dashboard: https://supabase.com/dashboard
-- 2. Select your Project -> Click "SQL Editor" in the left sidebar
-- 3. Click "New Query", paste this entire script, and click "RUN"
-- ==============================================================================

-- 1. Create table for storing validated ideas & activity logs
create table if not exists public.idea_validations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  user_email text,
  idea_title text not null,
  idea text not null,
  domain text,
  target_customer text,
  validation_type text default 'all',
  viability_score integer default 85,
  feasibility_score numeric default 7.5,
  summary text,
  full_result jsonb not null default '{}'::jsonb,
  is_starred boolean default false,
  tags text[] default array[]::text[],
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Enable Row Level Security (RLS)
alter table public.idea_validations enable row level security;

-- 3. RLS Policies
-- Allow read:
drop policy if exists "Enable read access for validations" on public.idea_validations;
create policy "Enable read access for validations"
  on public.idea_validations
  for select
  using (true);

-- Allow insert:
drop policy if exists "Enable insert access for validations" on public.idea_validations;
create policy "Enable insert access for validations"
  on public.idea_validations
  for insert
  with check (true);

-- Allow update:
drop policy if exists "Enable update access for validations" on public.idea_validations;
create policy "Enable update access for validations"
  on public.idea_validations
  for update
  using (true);

-- Allow delete:
drop policy if exists "Enable delete access for validations" on public.idea_validations;
create policy "Enable delete access for validations"
  on public.idea_validations
  for delete
  using (true);

-- 4. High-performance Indexes
create index if not exists idx_validations_user_id on public.idea_validations(user_id);
create index if not exists idx_validations_created_at on public.idea_validations(created_at desc);
create index if not exists idx_validations_starred on public.idea_validations(is_starred);
create index if not exists idx_validations_domain on public.idea_validations(domain);

-- 5. Updated At Trigger
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = timezone('utc'::text, now());
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_updated_at on public.idea_validations;
create trigger set_updated_at
  before update on public.idea_validations
  for each row
  execute function public.handle_updated_at();

-- Schema setup complete!
