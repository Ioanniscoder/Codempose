\version "2.24.1"
\language "english"
\header
{
    title = "first_score_all (generated)"
    composer = "Python + music21 + Abjad"
}
\score
{
    % OPEN_BRACKETS:
    \new Score
    <<
        % OPEN_BRACKETS:
        \new PianoStaff
        <<
            % OPEN_BRACKETS:
            \context Staff = "Melody1"
            {
                % OPEN_BRACKETS:
                \context Voice = "Melody1"
                {
                    % BEFORE:
                    % COMMANDS:
                    \key c \major
                    \set Staff.midiInstrument = #"acoustic grand piano"
                    \tempo 4=100
                    % OPENING:
                    % COMMANDS:
                    \clef "treble"
                    \time 4/4
                    e''4
                    d''4
                    c''4
                    b'4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            \context Staff = "Harmony"
            {
                % OPEN_BRACKETS:
                \context Voice = "Harmony"
                {
                    % BEFORE:
                    % COMMANDS:
                    \set Staff.midiInstrument = #"acoustic bass"
                    % OPENING:
                    % COMMANDS:
                    \clef "bass"
                    \time 4/4
                    e'2
                    b'2
                    <e' g' b'>1
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            \context Staff = "Melody2"
            {
                % OPEN_BRACKETS:
                \context Voice = "Melody2"
                {
                    % BEFORE:
                    % COMMANDS:
                    \set Staff.midiInstrument = #"acoustic grand piano"
                    e'4
                    d'4
                    c'4
                    b4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            \context Staff = "Melody3"
            {
                % OPEN_BRACKETS:
                \context Voice = "Melody3"
                {
                    % BEFORE:
                    % COMMANDS:
                    \set Staff.midiInstrument = #"acoustic grand piano"
                    e'4
                    d'4
                    c'4
                    b4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
            % OPEN_BRACKETS:
            \context Staff = "Melody4"
            {
                % OPEN_BRACKETS:
                \context Voice = "Melody4"
                {
                    % BEFORE:
                    % COMMANDS:
                    \set Staff.midiInstrument = #"acoustic grand piano"
                    e'4
                    d'4
                    d'4
                    c'4
                % CLOSE_BRACKETS:
                }
            % CLOSE_BRACKETS:
            }
        % CLOSE_BRACKETS:
        >>
    % CLOSE_BRACKETS:
    >>
    \layout
    {
        % layout settings: use defaults, but keep block so Frescobaldi shows engraving options
    }
    \midi
    {
        \tempo 4 = 100
        % Default MIDI settings - adjust instruments/positions as needed
    }
}
