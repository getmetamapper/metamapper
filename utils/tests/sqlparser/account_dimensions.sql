select *
from fpaa.daily_arr
limit 1

-------------OLD REDSHIFT AND ACCOUNT-BASED CODE--------------------------


-- with

-- stripe1 as ( -- find all workspaces that have ever been BT in Stripe
--       select  distinct workspace_id
--         from  citrus.workspaces_master  -- current ETL
--       where  stripe_plan_tier = 'Business'
--       UNION
--       select  distinct group_id
--         from  etl3.groups               -- old ETL
--       where  billing_plan_id in ('enterprise-$0-1-year',
--                                 'team-$0',
--                                 'warehouses-advanced-$0',
--                                 'iroko',
--                                 'growth-attictv',
--                                 'integrations-growth-$0',
--                                 'warehouses-business-$0',
--                                 'integrations-business-$0',
--                                 'business')
--       UNION
--       select  distinct group_id
--         from  etl.groups                -- even older ETL
--       where  account_billing_plan in ('Enterprise')
-- ),

-- ss1 as (    -- find first & last date in SS for great connector
--       select  workspace_id, min(date) as ss_start, --workspace ID is the actual mongo workspaceID
--               max(case when total_arr > 0 then date end) as ss_churn
--         from  fpaa_restricted.ss_daily_arr--_no_gaps
--     group by  1
-- ),

-- -- bt as (     -- find first and last day on BT for great connector
-- --       select  account_id,
-- --               min(date)::datetime as bt_start,
-- --               max(case when arr <= 1 and opportunity_ids is not null then date else null END) as bt_churn
-- --         from  fpaa_restricted.bt_daily_arr
-- --     group by  1
-- -- ),

-- list as (   -- create row numbers for BT opps so we can keep the first one later
--     select *
--     from (
--       select  distinct account_id, id as opportunity_id, close_date, earliest_recognize_date_c,
--                 row_number() over (partition by account_id order by close_date, opportunity_id) as row_number
--         from  salesforce.opportunities as o
--       where  plan_c = 'Business'
--         and  (is_won or (renewal_opportunity_c = 'Renewal' and is_closed and stage_name <> 'Closed - Duplicate Record'))
--         and  not is_deleted
--         and  id <> '0063100000g7KwEAAU' -- 'Real' deal is not CARR
--         and  account_id <> '001i000001SnYGWAA3' -- LV310 is a reneg churned account, but does not have a churned opportunity
--         and  account_id <> '0013100001kPDNrAAO' -- John's test account
--         and  account_id <> '001i000001JTYh5AAH' -- Watsi
--         and  renewal_opportunity_c <> 'Credit'
--     )
--     where  row_number = 1
--       and  close_date::date > '2018-09-30'::date
--       --**EK: This grabs list of BT accounts for which first opp closed is after 9/30/2018
-- ),


-- gc_prep1 as (
--       select  sw.workspace_id_c::text as workspace_id, w.slug::text,
--               case when sw.workspace_id_c = 'GXDTK99ZHz'
--                   then '0013100001npNUsAAM' else sw.account_c end::text as account_id,
--               created::date, --ss_churn, bt_start,
--               3 as priority
--         from  salesforce.workspaces as sw
--         join  mongo.workspaces as w
--           on  w.id = sw.workspace_id_c
--   left join  stripe1 as s
--           on  s.workspace_id = sw.workspace_id_c
--         join  ss1 as ss -- excludes workspaces that were never paying SS
--           on  ss.workspace_id = sw.workspace_id_c
--       where  case when sw.workspace_id_c = 'GXDTK99ZHz' then '0013100001npNUsAAM' else sw.account_c end is not null
--         -- and  (s.workspace_id is not null                         -- workspace must have been BT in Stripe at some point
--         --       or bt_start >= date_add('day', -60, convert_timezone('US/Pacific', localtimestamp)::date))  -- or BT deal must have closed in last 60 days
--         and  abs(date_diff('day', ss_churn, convert_timezone('US/Pacific', localtimestamp)::date )) <= 90     -- workspace must have churned from SS with 90 days (before or after) of BT start
--         -- and  (case when ss_start > bt_start and (bt_churn is null or ss_start < bt_churn)
--         --           then 1 else 0 end) = 0                          -- excludes SS workspaces that started paying after start of BT contract
--       union
--       select  m.workspace_id::text, m.slug::text,
--               (case when m.workspace_id = 'GXDTK99ZHz' then '0013100001npNUsAAM'
--                       else m.account_id end)::text as account_id,
--               created::date, --ss_churn, bt_start,
--               1 as priority
--         from  sandbox_calbanese.ss_bt_mapping_2018_08_27 as m
--         join  mongo.workspaces as w
--           on  w.id = m.workspace_id
--   left join  stripe1 as s
--           on  s.workspace_id = m.workspace_id
--         join  ss1 as ss -- excludes workspaces that were never paying SS
--           on  ss.workspace_id = m.workspace_id
--       where  m.account_id is not null
--         and  m.workspace_id is not null
--         -- and  (s.workspace_id is not null                         -- workspace must have been BT in Stripe at some point
--         --       or bt_start >= date_add('day', -60, convert_timezone('US/Pacific', localtimestamp)::date))  -- or BT deal must have closed in last 60 days
--         and  abs(date_diff('day', ss_churn, convert_timezone('US/Pacific', localtimestamp)::date)) <= 90     -- workspace must have churned from SS with 90 days (before or after) of BT start
--         -- and  (case when ss_start > bt_start and (bt_churn is null or ss_start < bt_churn)
--         --           then 1 else 0 end) = 0                          -- excludes SS workspaces that started paying after start of BT contract
--         and  m.workspace_id not in ('xkVZL9ZDut')                -- edge case that shouldn't count
--       union
--       select  w.workspace_id_c::text as workspace_id, w2.slug::text, b.account_c::text as account_id,
--               w2.created::date, --ss_churn, bt_start,
--               2 as priority
--         from  salesforce.workspaces as w
--   left join  salesforce.billings as b
--           on  b.id = w.link_to_current_bill_c
--   left join  mongo.workspaces as w2
--           on  w2.id = w.workspace_id_c
--   left join  stripe1 as s
--           on  s.workspace_id = w.workspace_id_c
--         join  ss1 as ss -- excludes workspaces that were never paying SS
--           on  ss.workspace_id = w.workspace_id_c
--       where
--               -- (s.workspace_id is not null                         -- workspace must have been BT in Stripe at some point
--               -- or bt_start >= date_add('day', -60, convert_timezone('US/Pacific', localtimestamp)::date)) and -- or BT deal must have closed in last 60 days
--               abs(date_diff('day', ss_churn, convert_timezone('US/Pacific', localtimestamp)::date)) <= 90     -- workspace must have churned from SS with 90 days (before or after) of BT start
--         -- and  (case when ss_start > bt_start and (bt_churn is null or ss_start < bt_churn)
--         --           then 1 else 0 end) = 0                          -- excludes SS workspaces that started paying after start of BT contract
--         and  b.account_c is not null
--         and  w.workspace_id_c is not null
-- ),

-- gc_prep2 as ( -- create row numbers for accounts with more than one upsold SS --> BT workspace
--       select  g.*, row_number() over (partition by account_id order by priority, created) as rn
--         from  gc_prep1 as g
--       where  (account_id + '-' + workspace_id <> '001i000001KeEfyAAF-x7unvviph2')  -- drop a link that is incorrect

-- )

-- select  workspace_id, slug, account_id, case priority when 1 then 'Manual Finance Review' when 2 then 'Billing' else 'SFDC Workspaces' end as Source
--   from  gc_prep2
-- where  rn = 1
-- --Exclude potential mappings for accounts that already have Upsell recognized, or BT contract started >60 days ago
--   and  account_id not in (
--           select distinct account_id
--             from fpaa_restricted.ss_to_bt_upsell_connector --BT accounts that already have upsell mapping
--           where bt_start <= '2020-01-31'::date --trying to look at upsell-mapping through EoM November

--           UNION

--           select  account_id
--             from  fpaa_restricted.bt_daily_arr
--         group by  1
--         -- having min(date)::datetime < date_add('day', -60, convert_timezone('US/Pacific', localtimestamp)::date) --BT accounts starting more than 60days ago
--           having  min(date)::datetime < date_add('day', -60, '2020-01-31'::date) --BT accounts starting more than 60days ago from EoM November
--         )
-- {"user":"@liz_hartmann07","email":"liz.hartmann@segment.com","url":"https://modeanalytics.com/segment/reports/691020cc12fc/runs/032ca26aabe4/queries/2edad214d9d0","scheduled":true}
