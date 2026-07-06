import sys
import os
import subprocess
import cozmo
from dotenv import load_dotenv

load_dotenv()

DEVICE_1 = os.getenv("DEVICE_1_ID")
DEVICE_2 = os.getenv("DEVICE_2_ID")


def build_android_connector(device_id):
    try:
        import cozmo.run as cozmo_run
        connector_cls = getattr(cozmo_run, "AndroidConnector", None)
    except Exception:
        connector_cls = None

    if connector_cls is None:
        raise RuntimeError("AndroidConnector is not available in this Cozmo SDK build.")

    candidate_kwargs = (
        {"device_id": device_id},
        {"serial": device_id},
        {"adb_device": device_id},
        {"adb_serial": device_id},
        {"android_device_id": device_id},
    )

    for kwargs in candidate_kwargs:
        try:
            return connector_cls(**kwargs)
        except TypeError:
            continue

    try:
        return connector_cls(device_id)
    except TypeError:
        raise RuntimeError("Could not construct AndroidConnector with this SDK version.")


def clear_adb_forwards(device_id):
    # Ignore failures; just best-effort cleanup of stale port-forwards.
    subprocess.call(["adb", "-s", device_id, "forward", "--remove-all"])


def run_speech(device_id, label, text):
    print("[INIT] {} connecting on device {}...".format(label, device_id))
    clear_adb_forwards(device_id)
    connector = build_android_connector(device_id)

    def program(robot):
        print("[ACTION] {} connected, preparing robot...".format(label))
        robot.set_robot_volume(1.0)
        robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()
        robot.set_lift_height(0.0).wait_for_completed()

        for attempt in (1, 2):
            print("[ACTION] {} attempt {} says: {}".format(label, attempt, text))
            action = robot.say_text(
                text,
                use_cozmo_voice=True,
                play_excited_animation=False,
            )

            try:
                action.wait_for_completed(timeout=8)
            except Exception as e:
                print("[WARN] {} speech wait exception: {}".format(label, e))

            print("[RESULT] {} speech action state={}, succeeded={}".format(
                label, action.state, action.has_succeeded
            ))

            if action.has_succeeded:
                return

        failure_code = getattr(action, "failure_code", None)
        failure_reason = getattr(action, "failure_reason", None)
        print("[ERROR] {} speech failed twice. code={} reason={}".format(
            label, failure_code, failure_reason
        ))

    cozmo.run_program(program, connector=connector, use_3d_viewer=False, use_viewer=False)


def main():
    if not DEVICE_1 or not DEVICE_2:
        print("[ERROR] Missing DEVICE_1_ID or DEVICE_2_ID in .env")
        sys.exit(1)

    run_speech(DEVICE_2, "COZMO 2", "I am cozmo 2")
    run_speech(DEVICE_1, "COZMO 1", "I am cozmo 1")

    print("[DONE] Both robots spoke.")


if __name__ == "__main__":
    main()