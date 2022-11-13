from pony.orm import db_session, select

from app.models.match import Match
from app.models.robot_result import RobotMatchResult
from app.schemas.match import Host, MatchResponse, RobotInMatch, RobotResult
from app.util.assets import get_robot_avatar, get_user_avatar
from app.util.status_codes import MATCH_NOT_FOUND_ERROR


def match_id_to_schema(match_id: int):
    robots = {}
    with db_session:
        match = Match.get(id=match_id)
        if not match:
            raise MATCH_NOT_FOUND_ERROR
        for r in match.plays:
            r_avatar = get_robot_avatar(r)
            robots[r.id] = RobotInMatch(
                name=r.name, avatar_url=r_avatar, username=r.owner.name
            )

        results = None
        if match.state == "Finished":
            robot_results = select(
                r for r in RobotMatchResult if r.match_id == match.id
            )
            results = {
                r.robot_id: RobotResult(
                    robot_pos=r.position,
                    death_count=r.death_count,
                )
                for r in robot_results
            }

        h_avatar = get_user_avatar(match.host)
        return MatchResponse(
            id=match.id,
            host=Host(username=match.host.name, avatar_url=h_avatar),
            name=match.name,
            max_players=match.max_players,
            min_players=match.min_players,
            games=match.game_count,
            rounds=match.round_count,
            state=match.state,
            is_private=match.password != "",
            robots=robots,
            results=results,
        )
