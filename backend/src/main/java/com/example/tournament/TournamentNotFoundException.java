package com.example.tournament;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.NOT_FOUND)
public class TournamentNotFoundException extends RuntimeException {
    public TournamentNotFoundException(Long tournamentId) {
        super("Tournament with ID " + tournamentId + " not found for duel with ID " + tournamentId);
    }
}