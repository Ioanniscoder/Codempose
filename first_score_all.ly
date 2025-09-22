\version "2.24.1"
\language "english"
\header
{
    title = "first_score_all (generated)"
    composer = "Python + music21 + Abjad"
}
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
                \tempo 4=100
                % OPENING:
                % COMMANDS:
                \clef "treble"
                \time 4/4
                e''2
                b'4
                e''4
                e''2
                f''4
                e''4
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
