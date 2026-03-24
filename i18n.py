"""
RunnerMatch - Internationalization (i18n)
Bilingual support: Spanish (es) and English (en).
"""

import streamlit as st

TRANSLATIONS = {
    # =========================================================================
    # GENERAL
    # =========================================================================
    "app_name": {"es": "RunnerMatch", "en": "RunnerMatch"},
    "app_tagline": {
        "es": "Conecta con corredores verificados",
        "en": "Connect with verified runners",
    },
    "language": {"es": "Idioma", "en": "Language"},
    "save": {"es": "Guardar", "en": "Save"},
    "cancel": {"es": "Cancelar", "en": "Cancel"},
    "submit": {"es": "Enviar", "en": "Submit"},
    "back": {"es": "Volver", "en": "Back"},
    "next": {"es": "Siguiente", "en": "Next"},
    "loading": {"es": "Cargando...", "en": "Loading..."},
    "success": {"es": "Completado", "en": "Success"},
    "error": {"es": "Error", "en": "Error"},
    "required_field": {"es": "Campo obligatorio", "en": "Required field"},

    # =========================================================================
    # AUTH
    # =========================================================================
    "login": {"es": "Iniciar Sesión", "en": "Log In"},
    "signup": {"es": "Registrarse", "en": "Sign Up"},
    "logout": {"es": "Cerrar Sesión", "en": "Log Out"},
    "email": {"es": "Correo electrónico", "en": "Email"},
    "password": {"es": "Contraseña", "en": "Password"},
    "confirm_password": {"es": "Confirmar contraseña", "en": "Confirm Password"},
    "forgot_password": {"es": "¿Olvidaste tu contraseña?", "en": "Forgot password?"},
    "reset_password": {"es": "Restablecer contraseña", "en": "Reset Password"},
    "no_account": {"es": "¿No tienes cuenta?", "en": "Don't have an account?"},
    "have_account": {"es": "¿Ya tienes cuenta?", "en": "Already have an account?"},
    "password_mismatch": {"es": "Las contraseñas no coinciden", "en": "Passwords don't match"},
    "email_exists": {
        "es": "Este correo ya está registrado",
        "en": "This email is already registered",
    },
    "weak_password": {
        "es": "La contraseña debe tener al menos 6 caracteres",
        "en": "Password must be at least 6 characters",
    },
    "invalid_credentials": {
        "es": "Correo o contraseña incorrectos",
        "en": "Invalid email or password",
    },
    "reset_email_sent": {
        "es": "Se envió un enlace de restablecimiento a tu correo",
        "en": "Password reset link sent to your email",
    },
    "verification_email_sent": {
        "es": "Se envió un correo de verificación. Revisa tu bandeja.",
        "en": "Verification email sent. Check your inbox.",
    },

    # =========================================================================
    # PROFILE
    # =========================================================================
    "profile": {"es": "Perfil", "en": "Profile"},
    "edit_profile": {"es": "Editar Perfil", "en": "Edit Profile"},
    "first_name": {"es": "Nombre", "en": "First Name"},
    "last_name": {"es": "Apellido", "en": "Last Name"},
    "display_name": {"es": "Nombre a mostrar", "en": "Display Name"},
    "bio": {"es": "Sobre mí", "en": "About Me"},
    "gender": {"es": "Género", "en": "Gender"},
    "gender_male": {"es": "Hombre", "en": "Male"},
    "gender_female": {"es": "Mujer", "en": "Female"},
    "gender_other": {"es": "Otro", "en": "Other"},
    "looking_for": {"es": "Busco", "en": "Looking For"},
    "looking_male": {"es": "Hombres", "en": "Men"},
    "looking_female": {"es": "Mujeres", "en": "Women"},
    "looking_both": {"es": "Ambos", "en": "Both"},
    "birth_date": {"es": "Fecha de nacimiento", "en": "Date of Birth"},
    "city": {"es": "Ciudad", "en": "City"},
    "country": {"es": "País", "en": "Country"},
    "height_cm": {"es": "Altura (cm)", "en": "Height (cm)"},
    "weight_kg": {"es": "Peso (kg)", "en": "Weight (kg)"},
    "bmi": {"es": "IMC", "en": "BMI"},
    "photos": {"es": "Fotos", "en": "Photos"},
    "upload_photo": {"es": "Subir foto", "en": "Upload Photo"},
    "primary_photo": {"es": "Foto principal", "en": "Primary Photo"},
    "profile_complete": {
        "es": "Tu perfil está completo",
        "en": "Your profile is complete",
    },
    "profile_incomplete": {
        "es": "Completa tu perfil para empezar a buscar",
        "en": "Complete your profile to start matching",
    },

    # =========================================================================
    # RUNNING STATS
    # =========================================================================
    "running_stats": {"es": "Estadísticas de Running", "en": "Running Stats"},
    "preferred_distance": {"es": "Distancia preferida", "en": "Preferred Distance"},
    "avg_pace": {"es": "Ritmo promedio (min/km)", "en": "Average Pace (min/km)"},
    "years_running": {"es": "Años corriendo", "en": "Years Running"},
    "weekly_km": {"es": "Km por semana", "en": "Weekly Km"},
    "dist_5k": {"es": "5K", "en": "5K"},
    "dist_10k": {"es": "10K", "en": "10K"},
    "dist_21k": {"es": "Media Maratón (21K)", "en": "Half Marathon (21K)"},
    "dist_42k": {"es": "Maratón (42K)", "en": "Marathon (42K)"},
    "dist_trail": {"es": "Trail", "en": "Trail"},
    "dist_ultra": {"es": "Ultra Trail", "en": "Ultra Trail"},

    # =========================================================================
    # RACE VERIFICATION
    # =========================================================================
    "verify_race": {"es": "Verificar Carrera", "en": "Verify Race"},
    "select_race": {"es": "Selecciona tu carrera", "en": "Select Your Race"},
    "your_full_name": {
        "es": "Tu nombre completo (como aparece en la inscripción)",
        "en": "Your full name (as it appears on registration)",
    },
    "bib_number": {"es": "Número de dorsal", "en": "Bib Number"},
    "verify_button": {"es": "Verificar mi inscripción", "en": "Verify My Registration"},
    "verification_success": {
        "es": "¡Verificación exitosa! Eres un corredor verificado.",
        "en": "Verification successful! You are a verified runner.",
    },
    "verification_pending": {
        "es": "Tu verificación está pendiente de revisión.",
        "en": "Your verification is pending review.",
    },
    "verification_failed": {
        "es": "No pudimos encontrarte en la lista de participantes. Verifica tu nombre.",
        "en": "We couldn't find you in the participant list. Please check your name.",
    },
    "already_verified": {
        "es": "Ya estás verificado para esta carrera.",
        "en": "You are already verified for this race.",
    },

    # =========================================================================
    # MATCHING
    # =========================================================================
    "discover": {"es": "Descubrir", "en": "Discover"},
    "like": {"es": "Me gusta", "en": "Like"},
    "pass": {"es": "Pasar", "en": "Pass"},
    "its_a_match": {"es": "¡Es un Match!", "en": "It's a Match!"},
    "match_message": {
        "es": "Tú y {name} se han gustado mutuamente",
        "en": "You and {name} liked each other",
    },
    "send_message": {"es": "Enviar mensaje", "en": "Send Message"},
    "no_more_profiles": {
        "es": "No hay más perfiles por ahora. ¡Vuelve pronto!",
        "en": "No more profiles right now. Come back soon!",
    },
    "must_be_verified": {
        "es": "Debes verificar tu carrera para empezar a buscar",
        "en": "You must verify your race to start matching",
    },

    # =========================================================================
    # CHAT
    # =========================================================================
    "messages": {"es": "Mensajes", "en": "Messages"},
    "matches": {"es": "Matches", "en": "Matches"},
    "type_message": {"es": "Escribe un mensaje...", "en": "Type a message..."},
    "no_matches": {
        "es": "Aún no tienes matches. ¡Sigue explorando!",
        "en": "No matches yet. Keep exploring!",
    },
    "no_messages": {
        "es": "No hay mensajes aún. ¡Di hola!",
        "en": "No messages yet. Say hi!",
    },

    # =========================================================================
    # ADMIN
    # =========================================================================
    "admin_panel": {"es": "Panel de Administración", "en": "Admin Panel"},
    "manage_races": {"es": "Gestionar Carreras", "en": "Manage Races"},
    "add_race": {"es": "Agregar Carrera", "en": "Add Race"},
    "upload_participants": {
        "es": "Subir lista de participantes",
        "en": "Upload Participant List",
    },
    "scrape_results": {"es": "Buscar resultados en web", "en": "Scrape Results from Web"},
    "race_name": {"es": "Nombre de la carrera", "en": "Race Name"},
    "race_date": {"es": "Fecha de la carrera", "en": "Race Date"},
    "total_participants": {"es": "Total participantes", "en": "Total Participants"},
    "pending_verifications": {
        "es": "Verificaciones pendientes",
        "en": "Pending Verifications",
    },
    "user_management": {"es": "Gestión de Usuarios", "en": "User Management"},
    "total_users": {"es": "Total usuarios", "en": "Total Users"},
    "verified_users": {"es": "Usuarios verificados", "en": "Verified Users"},
    "active_matches": {"es": "Matches activos", "en": "Active Matches"},
}


def t(key: str, **kwargs) -> str:
    """
    Get translation for current language.
    Usage: t("its_a_match")  or  t("match_message", name="Ana")
    """
    lang = st.session_state.get("language", "es")
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang, entry.get("es", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def language_selector():
    """Render a compact language toggle."""
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🇪🇸 Español", use_container_width=True,
                      disabled=st.session_state.get("language") == "es"):
            st.session_state.language = "es"
            st.rerun()
    with col2:
        if st.button("🇺🇸 English", use_container_width=True,
                      disabled=st.session_state.get("language") == "en"):
            st.session_state.language = "en"
            st.rerun()
