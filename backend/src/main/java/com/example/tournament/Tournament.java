package com.example.tournament;

import com.example.duel.Duel;
import com.fasterxml.jackson.annotation.*;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.util.List;
import java.time.LocalDateTime;
import java.sql.Date;
import java.sql.Time;

@Entity
@Table(name = "tournament")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class Tournament {
    @Id @GeneratedValue(strategy = GenerationType.AUTO) private Long tournament_id;
    @NotNull private String name;
    @JsonProperty("isRandom") private boolean isRandom;
    private Date date;
    private Time time;
    private String location;
    private Long organizer_id;
    @Size(max = 255) private String description;
    private LocalDateTime modifiedAt = LocalDateTime.now(); // Default to current time

    @OneToMany(mappedBy = "tournament", cascade = CascadeType.ALL, orphanRemoval = true) 
    @JsonIgnore
    private List<Duel> duels;

    public Tournament(String name, boolean isRandom, Date date, Time time, String location, Long organizer_id, String description) {
        this.name = name;
        this.isRandom = isRandom;
        this.date = date;
        this.time = time;
        this.location = location;
        this.organizer_id = organizer_id;
        this.description = description;
    }

    public Long getTournamentId() {
        return tournament_id;
    }
    
    public boolean getIsRandom() {
        return isRandom;
    }

    public void setIsRandom(boolean isRandom) {
        this.isRandom = isRandom;
    }

    public Long getOrganizer() {
        return organizer_id;
    }

    public void setOrganizer(Long organizer_id) {
        this.organizer_id = organizer_id;
    }

    public Long getTournamentId(Long tournament_id){
        return tournament_id;
    }

    public void setTournamentId (Long tournament_id){
        this.tournament_id = tournament_id;
    }


}