from fastapi import HTTPException

USER_NOT_FOUND_ERROR = HTTPException(status_code=404, detail="User not found")

USER_NOT_VERIFIED_ERROR = HTTPException(status_code=403, detail="User is not verified")

USER_WAS_NOT_IN_MATCH_ERROR = HTTPException(
    status_code=403, detail="User was not in match"
)

ROBOT_NOT_FOUND_ERROR = HTTPException(status_code=404, detail="Robot not found")

ROBOT_EXISTS_FOR_USER = HTTPException(
    status_code=409, detail="Robot with same name already exists for user"
)

ROBOT_NOT_FROM_USER_ERROR = HTTPException(
    status_code=403, detail="Robot does not belong to user"
)

MATCH_CAN_ONLY_BE_STARTED_BY_HOST_ERROR = HTTPException(
    status_code=403, detail="Host must start the match"
)

MATCH_CANNOT_BE_LEFT_BY_HOST_ERROR = HTTPException(
    status_code=403, detail="Host cannot leave own match"
)

MATCH_FULL_ERROR = HTTPException(status_code=403, detail="Match is full")

MATCH_MINIMUM_PLAYERS_NOT_REACHED_ERROR = HTTPException(
    status_code=403, detail="The minimum number of players was not reached"
)

MATCH_NOT_FOUND_ERROR = HTTPException(status_code=404, detail="Match not found")

MATCH_STARTED_ERROR = HTTPException(status_code=403, detail="Match has already started")

MATCH_PASSWORD_INCORRECT_ERROR = HTTPException(
    status_code=403, detail="Match password is incorrect"
)

ROBOT_CODE_UNSAFE_ERROR = HTTPException(
    status_code=418,
    detail="Forbidden functions or imports found in code",
)

ROBOT_CODE_SYNTAX_ERROR = HTTPException(
    status_code=418,
    detail="Syntax error",
)

ROBOT_CODE_CLASSES_ERROR = HTTPException(
    status_code=418,
    detail="Code must define exactly one class that inherits from Robot",
)

ROBOT_CODE_WAW_ERROR = HTTPException(
    status_code=418,
    detail="Invalid name for method or attribute of robot",
)

ROBOT_CODE_UNIMPLEMENTED_ERROR = HTTPException(
    status_code=418,
    detail="Methods initialize or respond not implemented",
)

INVALID_PICTURE_FORMAT_ERROR = HTTPException(
    status_code=422, detail="invalid picture format"
)

INVALID_TOKEN_ERROR = HTTPException(status_code=401, detail="Invalid token")

NON_EXISTANT_USER_OR_PASSWORD_ERROR = HTTPException(
    status_code=401, detail="Non existant user or password is incorrect"
)

VALUE_NOT_VALID_PASSWORD = HTTPException(
    status_code=422, detail="value is not a valid password"
)

CURRENT_PASSWORD_EQUAL_NEW_PASSWORD = HTTPException(
    status_code=409, detail="The current password is equal to the new password"
)

EMAIL_DOESNT_BELONG_TO_USER = HTTPException(
    status_code=401, detail="Email does not belong to any user"
)
