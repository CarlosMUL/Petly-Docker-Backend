package petly.sanosysalvos.cl.usuarios.Config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class SecurityConfig {

    private final JwtFilter jwtFilter; // Inyecta el filtro que creamos antes

    public SecurityConfig(JwtFilter jwtFilter) {
        this.jwtFilter = jwtFilter;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .cors(cors -> {}) // Habilita CORS con la configuración que definimos en CorsConfig
                .csrf(csrf -> csrf.disable()) // importante para APIs
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) //Spring NO va a crear ni mantener sesiones en el servidor.
                .authorizeHttpRequests(auth -> auth
                        // Rutas públicas (cualquiera puede acceder SIN token)
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                        .requestMatchers("/petly/usuarios/registrar", "/petly/auth/login").permitAll()
                        // Todo lo demás requiere autenticación (tener token válido)
                        .anyRequest().authenticated()
                        
                )
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class); // Agrega nuestro filtro antes del filtro de autenticación de Spring Security

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

}