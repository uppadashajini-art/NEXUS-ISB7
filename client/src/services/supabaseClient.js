import { createClient } from "@supabase/supabase-js";

// Storage keys
const SUPABASE_URL_KEY = "nexus_supabase_url";
const SUPABASE_ANON_KEY = "nexus_supabase_anon_key";
const LOCAL_ACTIVITIES_KEY = "nexus_local_activities";
const ACTIVE_USER_KEY = "nexus_active_user";

// User's configured live Supabase credentials
export const DEFAULT_SUPABASE_URL =
  "https://nopyphwaagojntlfbkol.supabase.co";

export const DEFAULT_PUBLISHABLE_KEY =
  "sb_publishable_tWxGmcPMMAl8rGPnklvkWg_ncO-DZzk";

/**
 * Get active Supabase configuration (from env or localStorage)
 */
export function getSupabaseConfig() {
  const envUrl =
    import.meta.env.VITE_SUPABASE_URL || DEFAULT_SUPABASE_URL;

  const envAnonKey =
    import.meta.env.VITE_SUPABASE_ANON_KEY ||
    DEFAULT_PUBLISHABLE_KEY;

  const storedUrl =
    typeof window !== "undefined"
      ? localStorage.getItem(SUPABASE_URL_KEY) || ""
      : "";

  const storedAnonKey =
    typeof window !== "undefined"
      ? localStorage.getItem(SUPABASE_ANON_KEY) || ""
      : "";

  const url = (storedUrl || envUrl).trim();

  const anonKey = (
    storedAnonKey ||
    envAnonKey ||
    DEFAULT_PUBLISHABLE_KEY
  ).trim();

  const isConfigured = Boolean(
    url &&
      anonKey &&
      url.startsWith("https://") &&
      url.includes("supabase.co") &&
      (anonKey.startsWith("sb_publishable_") ||
        anonKey.length > 20)
  );

  return {
    url,
    anonKey,
    isConfigured,
    source: storedUrl
      ? "custom"
      : envUrl
      ? "env"
      : "key_ready",
  };
}

/**
 * Save user custom Supabase credentials
 */
export function saveSupabaseConfig(url, anonKey) {
  if (typeof window !== "undefined") {
    if (url) {
      localStorage.setItem(
        SUPABASE_URL_KEY,
        url.trim()
      );
    } else {
      localStorage.removeItem(SUPABASE_URL_KEY);
    }

    if (anonKey) {
      localStorage.setItem(
        SUPABASE_ANON_KEY,
        anonKey.trim()
      );
    } else {
      localStorage.removeItem(SUPABASE_ANON_KEY);
    }
  }

  // Re-instantiate client
  initSupabaseClient();

  return getSupabaseConfig();
}

// Active client instance
let supabaseInstance = null;

export function initSupabaseClient() {
  const config = getSupabaseConfig();

  if (config.isConfigured) {
    try {
      supabaseInstance = createClient(
        config.url,
        config.anonKey,
        {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
          },
        }
      );

      console.log(
        "✅ Supabase client initialized with Project:",
        config.url
      );

      return supabaseInstance;
    } catch (err) {
      console.warn(
        "Failed to initialize Supabase client with provided credentials:",
        err
      );

      supabaseInstance = null;
    }
  } else {
    supabaseInstance = null;
  }

  return null;
}

// Initial setup
initSupabaseClient();

export function getSupabase() {
  if (!supabaseInstance) {
    initSupabaseClient();
  }

  return supabaseInstance;
}

// ==============================================================================
// AUTHENTICATION SERVICES
// ==============================================================================

/**
 * Sign up real user with email & password in Supabase Auth
 */
export async function signUpUser({
  email,
  password,
  fullName,
}) {
  const supabase = getSupabase();

  if (supabase) {
    const { data, error } =
      await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name:
              fullName || email.split("@")[0],

            avatar_url:
              `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(
                email
              )}`,
          },
        },
      });

    if (error) throw error;

    if (data.user) {
      localStorage.setItem(
        ACTIVE_USER_KEY,
        JSON.stringify(data.user)
      );
    }

    return {
      user: data.user,
      session: data.session,
      isLive: true,
    };
  }

  // If Supabase Project URL is not yet connected,
  // store active session so user is authenticated
  const activeUser = {
    id: `usr_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 6)}`,

    email,

    user_metadata: {
      full_name:
        fullName || email.split("@")[0],

      avatar_url:
        `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(
          email
        )}`,
    },

    created_at: new Date().toISOString(),
  };

  localStorage.setItem(
    ACTIVE_USER_KEY,
    JSON.stringify(activeUser)
  );

  return {
    user: activeUser,
    session: {
      access_token: "active-session-token",
    },
    isLive: false,
  };
}

/**
 * Sign in real user with email & password
 */
export async function signInUser({
  email,
  password,
}) {
  const supabase = getSupabase();

  if (supabase) {
    const { data, error } =
      await supabase.auth.signInWithPassword({
        email,
        password,
      });

    if (error) throw error;

    if (data.user) {
      localStorage.setItem(
        ACTIVE_USER_KEY,
        JSON.stringify(data.user)
      );
    }

    return {
      user: data.user,
      session: data.session,
      isLive: true,
    };
  }

  // Active session fallback if Project URL hasn't been pasted yet
  const stored =
    localStorage.getItem(ACTIVE_USER_KEY);

  let activeUser = null;

  if (stored) {
    try {
      activeUser = JSON.parse(stored);
      activeUser.email = email;
    } catch {
      activeUser = null;
    }
  }

  if (!activeUser) {
    activeUser = {
      id: `usr_${Date.now()}`,

      email,

      user_metadata: {
        full_name: email.split("@")[0],

        avatar_url:
          `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(
            email
          )}`,
      },

      created_at: new Date().toISOString(),
    };
  }

  localStorage.setItem(
    ACTIVE_USER_KEY,
    JSON.stringify(activeUser)
  );

  return {
    user: activeUser,
    session: {
      access_token: "active-session-token",
    },
    isLive: false,
  };
}

// ==============================================================================
// GOOGLE SIGN IN
// ==============================================================================

/**
 * Sign in with Google using Supabase OAuth
 */
export async function signInWithGoogleUser() {
  const supabase = getSupabase();

  if (!supabase) {
    throw new Error(
      "Supabase is not connected. Please configure Supabase first."
    );
  }

  const redirectUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}${window.location.pathname}`
      : undefined;

  const { data, error } =
    await supabase.auth.signInWithOAuth({
      provider: "google",

      options: {
        redirectTo: redirectUrl,
      },
    });

  if (error) {
    throw error;
  }

  return data;
}

// ==============================================================================
// SIGN OUT
// ==============================================================================

/**
 * Sign out
 */
export async function signOutUser() {
  const supabase = getSupabase();

  if (supabase) {
    await supabase.auth.signOut().catch(() => {});
  }

  localStorage.removeItem(ACTIVE_USER_KEY);

  return true;
}

// ==============================================================================
// CURRENT SESSION
// ==============================================================================

/**
 * Get current session & user
 */
export async function getCurrentSession() {
  const supabase = getSupabase();

  if (supabase) {
    try {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (!error && session?.user) {
        return {
          user: session.user,
          session,
          isLive: true,
        };
      }
    } catch (err) {
      console.warn(
        "Notice checking Supabase session:",
        err
      );
    }
  }

  // Check active user in local session
  const stored =
    localStorage.getItem(ACTIVE_USER_KEY);

  if (stored) {
    try {
      const user = JSON.parse(stored);

      return {
        user,
        session: {
          access_token: "active-token",
        },
        isLive: Boolean(supabase),
      };
    } catch {
      localStorage.removeItem(ACTIVE_USER_KEY);
    }
  }

  return {
    user: null,
    session: null,
    isLive: false,
  };
}

// ==============================================================================
// REAL DATABASE SAVING:
// IDEA VALIDATIONS & ACTIVITY LOGS
// ==============================================================================

function calculateViabilityScore(data) {
  let score = 82;

  const techScore =
    data?.technical_feasibility?.score;

  if (typeof techScore === "number") {
    score = Math.round(
      (score + techScore * 10) / 2
    );
  }

  const risks = Array.isArray(
    data?.risk_analysis
  )
    ? data.risk_analysis
    : [];

  if (risks.length > 3) {
    score = Math.max(50, score - 6);
  } else if (risks.length <= 1) {
    score = Math.min(96, score + 5);
  }

  const gaps =
    data?.competitor_analysis?.market_gaps;

  if (Array.isArray(gaps) && gaps.length >= 2) {
    score = Math.min(98, score + 4);
  }

  return Math.min(99, Math.max(60, score));
}

function deriveIdeaTitle(idea) {
  if (!idea) {
    return "Untitled Startup Concept";
  }

  const clean = idea
    .replace(/\n+/g, " ")
    .trim();

  if (clean.length <= 60) {
    return clean;
  }

  const firstSentence =
    clean.split(/[.?!]/)[0];

  return firstSentence.length <= 70
    ? firstSentence
    : clean.slice(0, 60) + "...";
}

/**
 * Real saving of validated idea
 * to Supabase Database table `idea_validations`
 */
export async function saveValidationActivity({
  userId,
  userEmail,
  idea,
  domain,
  targetCustomer,
  validationType,
  fullResult,
}) {
  const viabilityScore =
    calculateViabilityScore(fullResult);

  const feasibilityScore =
    fullResult?.technical_feasibility?.score ||
    7.5;

  const title = deriveIdeaTitle(idea);

  const summary =
    fullResult?.validation_report
      ?.executive_summary ||
    fullResult?.market_analysis
      ?.market_opportunity ||
    idea.slice(0, 160) + "...";

  const tags = [];

  if (domain) {
    tags.push(domain);
  }

  if (
    fullResult?.market_analysis?.industry &&
    fullResult.market_analysis.industry !== domain
  ) {
    tags.push(
      fullResult.market_analysis.industry
    );
  }

  if (targetCustomer) {
    tags.push(targetCustomer);
  }

  const newRecord = {
    id:
      typeof crypto !== "undefined" &&
      crypto.randomUUID
        ? crypto.randomUUID()
        : `log-${Date.now()}-${Math.random()
            .toString(36)
            .substr(2, 9)}`,

    user_id: String(
      userId || "authenticated_user"
    ),

    user_email:
      userEmail || "user@nexus.io",

    idea_title: title,

    idea: idea,

    domain:
      domain ||
      fullResult?.market_analysis?.industry ||
      "Tech / AI",

    target_customer:
      targetCustomer || "Target Audience",

    validation_type:
      validationType || "all",

    viability_score: viabilityScore,

    feasibility_score: feasibilityScore,

    summary: summary,

    full_result: fullResult,

    is_starred: false,

    tags: tags.slice(0, 5),

    created_at: new Date().toISOString(),

    updated_at: new Date().toISOString(),
  };

  // 1. Direct Supabase Database insert
  const supabase = getSupabase();

  let savedToSupabase = false;

  if (supabase) {
    try {
      const {
        data,
        error,
      } = await supabase
        .from("idea_validations")
        .insert({
          user_id: newRecord.user_id,

          user_email:
            newRecord.user_email,

          idea_title: title,

          idea: idea,

          domain: newRecord.domain,

          target_customer:
            newRecord.target_customer,

          validation_type:
            newRecord.validation_type,

          viability_score:
            viabilityScore,

          feasibility_score:
            feasibilityScore,

          summary: summary,

          full_result: fullResult,

          is_starred: false,

          tags: newRecord.tags,
        })
        .select()
        .single();

      if (!error && data) {
        newRecord.id = data.id;

        savedToSupabase = true;

        console.log(
          "🚀 Successfully saved record to Supabase database table `idea_validations`:",
          data.id
        );
      } else if (error) {
        console.error(
          "Supabase insert error:",
          error
        );
      }
    } catch (err) {
      console.error(
        "Supabase database insert exception:",
        err
      );
    }
  }

  // 2. Keep local mirror for instantaneous
  // offline and fast UI responsiveness
  saveToLocalActivities(newRecord);

  return {
    activity: newRecord,
    savedToSupabase,
  };
}

/**
 * Fetch all validation history for user
 * from Supabase database
 */
export async function fetchValidationActivities(
  userId
) {
  const supabase = getSupabase();

  let liveRecords = null;

  if (supabase) {
    try {
      let query = supabase
        .from("idea_validations")
        .select("*")
        .order("created_at", {
          ascending: false,
        });

      if (userId) {
        query = query.eq(
          "user_id",
          String(userId)
        );
      }

      const {
        data,
        error,
      } = await query;

      if (!error && Array.isArray(data)) {
        liveRecords = data;

        console.log(
          `📡 Loaded ${data.length} validated ideas from Supabase database.`
        );
      } else if (error) {
        console.warn(
          "Supabase query notice:",
          error.message
        );
      }
    } catch (err) {
      console.warn(
        "Supabase query exception, using local store:",
        err
      );
    }
  }

  if (
    liveRecords &&
    liveRecords.length > 0
  ) {
    saveBatchToLocalActivities(
      liveRecords
    );

    return liveRecords;
  }

  return getLocalActivities(userId);
}

/**
 * Toggle favorite in Supabase
 */
export async function toggleStarValidation(
  id,
  isStarred,
  userId
) {
  const supabase = getSupabase();

  if (supabase) {
    try {
      let query = supabase
        .from("idea_validations")
        .update({
          is_starred: isStarred,
        })
        .eq("id", id);

      if (userId) {
        query = query.eq(
          "user_id",
          String(userId)
        );
      }

      await query;
    } catch (err) {
      console.warn(
        "Could not update star in Supabase:",
        err
      );
    }
  }

  const list = getLocalActivities();

  const updated = list.map(
    (item) =>
      item.id === id
        ? {
            ...item,
            is_starred: isStarred,
          }
        : item
  );

  localStorage.setItem(
    LOCAL_ACTIVITIES_KEY,
    JSON.stringify(updated)
  );

  return isStarred;
}

/**
 * Delete validation log entry in Supabase
 */
export async function deleteValidationActivity(
  id,
  userId
) {
  const supabase = getSupabase();

  if (supabase) {
    try {
      let query = supabase
        .from("idea_validations")
        .delete()
        .eq("id", id);

      if (userId) {
        query = query.eq(
          "user_id",
          String(userId)
        );
      }

      await query;
    } catch (err) {
      console.warn(
        "Could not delete from Supabase:",
        err
      );
    }
  }

  const list = getLocalActivities();

  const updated = list.filter(
    (item) => item.id !== id
  );

  localStorage.setItem(
    LOCAL_ACTIVITIES_KEY,
    JSON.stringify(updated)
  );

  return true;
}

// ==============================================================================
// LOCAL STORAGE HELPERS
// ==============================================================================

function getLocalActivities(
  userId = null
) {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const raw = localStorage.getItem(
      LOCAL_ACTIVITIES_KEY
    );

    if (!raw) {
      return [];
    }

    const list = JSON.parse(raw);

    if (!Array.isArray(list)) {
      return [];
    }

    if (userId) {
      return list.filter(
        (item) =>
          String(item.user_id) ===
            String(userId) ||
          !item.user_id
      );
    }

    return list;
  } catch {
    return [];
  }
}

function saveToLocalActivities(record) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    const list = getLocalActivities();

    const filtered = list.filter(
      (item) => item.id !== record.id
    );

    filtered.unshift(record);

    localStorage.setItem(
      LOCAL_ACTIVITIES_KEY,
      JSON.stringify(
        filtered.slice(0, 100)
      )
    );
  } catch (err) {
    console.error(
      "Failed to save to local activities:",
      err
    );
  }
}

function saveBatchToLocalActivities(
  records
) {
  if (
    typeof window === "undefined" ||
    !Array.isArray(records)
  ) {
    return;
  }

  try {
    const existing =
      getLocalActivities();

    const map = new Map();

    existing.forEach((item) =>
      map.set(item.id, item)
    );

    records.forEach((item) =>
      map.set(item.id, item)
    );

    const merged = Array.from(
      map.values()
    ).sort(
      (a, b) =>
        new Date(b.created_at) -
        new Date(a.created_at)
    );

    localStorage.setItem(
      LOCAL_ACTIVITIES_KEY,
      JSON.stringify(
        merged.slice(0, 100)
      )
    );
  } catch (err) {
    console.error(
      "Failed to batch save local activities:",
      err
    );
  }
}