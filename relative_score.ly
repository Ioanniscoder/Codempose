\version "2.24.1"
\language "english"
\header
{
    title = "relative_score (generated)"
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
            \context Staff = "Melody"
            {
                % OPEN_BRACKETS:
                \context Voice = "Melody"
                {
                    % BEFORE:
                    % COMMANDS:
                    \key c \major
                    \tempo 4=100
                    % OPENING:
                    % COMMANDS:
                    \clef "treble"
                    \time 4/4
                    b''4
                    c'''4
                    d'''4
                    e'''4
                    <g''' b''' d''''>2.
                    r4
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
                    % OPENING:
                    % COMMANDS:
                    \clef "bass"
                    \time 4/4
                    c2
                    g2
                    <c' e' g'>1
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
