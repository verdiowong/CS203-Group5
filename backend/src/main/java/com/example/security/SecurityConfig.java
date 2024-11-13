package com.example.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;
import org.springframework.security.web.util.matcher.OrRequestMatcher;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private static final String[] ADMIN_MATCHERS = {
        "/tournament/?",
        "/tournament/**",
        "/duel/?",
        "/duel/**"
    };
    
    private static final String[] PERMIT_ALL_GETTERS = {
        "/tournament", 
        "/tournament/organizer", 
        "/tournament/search", 
        "/tournament/filter", 
        "/tournament/sorted", 
        "/tournament/matching", 
        "/duel", 
        "/duel/player/**"
    };
    
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // Authorize HTTP requests using the new authorizeHttpRequests method
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/register", "/auth/login").permitAll()
                .requestMatchers(new OrRequestMatcher(
                    // Allow POST requests to /profile without authentication
                    new AntPathRequestMatcher("/profile", "POST")
                )).permitAll()
                .requestMatchers("/api/duel/**").permitAll()
                .anyRequest().authenticated()
            )
            // Enable OAuth2 Resource Server and configure JWT validation
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(Customizer.withDefaults())
            );

        return http.build();
    }
}
