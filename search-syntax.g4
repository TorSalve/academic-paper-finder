grammar SimpleBoolean;

program: expression EOF;

expression
    : LPAREN expression RPAREN
    | expression op=AND expression
    | expression op=OR expression
    | op=NOT expression
    | FIELDTERM
    | SEARCHTERM
    ;
 
SEARCHTERM 
    : '"' TERM '"'
    | '\'' TERM '\''
    ;
    
fragment TERM : T*;
T: LETTER | DIGIT | SPECIAL | SPACE;

FIELD: 'title' | 'abstract' | 'full' | 'publication';

FIELDTERM: FIELD COLON SEARCHTERM;

LPAREN     : WS*'('WS* ;
RPAREN     : WS*')'WS* ;
COLON      : ':' ;
AND        : WS*'AND'WS*;
OR         : WS*'OR'WS*;
NOT        : 'NOT'WS ;
WS         : [ \r\t\u000C\n]+ -> skip;

SPACE: [ ];
SPECIAL: [-:?+=&];
LETTER: [a-zA-Z];
DIGIT: [0-9];