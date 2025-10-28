# ============================================================
# AutoVehicleRig_v14B_ConnectorMotor_UNIFIED2025_FIX2.py
# © 2025 Vincent Ilagan — TYMASTER / VFXVerse Studios
# Cinema 4D 2025.3.3 | Hybrid Suspension + Motor Drive (Unified Simulation)
# ============================================================

import c4d
from c4d import utils as u

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
WHEEL_NAMES = ["FL", "FR", "ML", "MR", "RL", "RR"]
AXLES = {
    "Front": ["FL", "FR"],
    "Mid": ["ML", "MR"],
    "Rear": ["RL", "RR"]
}

SUSP_LOWER = -100.0
SUSP_UPPER = 100.0
SUSP_STIFF = 4.0
SUSP_DAMP = 0.2
MOTOR_SPEED = 5.0
MOTOR_TORQUE = 50.0

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def find_obj(doc, name):
    return doc.SearchObject(name)

def make_null(name, color):
    n = c4d.BaseObject(c4d.Onull)
    n[c4d.ID_BASELIST_NAME] = name
    n[c4d.NULLOBJECT_DISPLAY] = 2
    n[c4d.ID_BASEOBJECT_USECOLOR] = 2
    n[c4d.ID_BASEOBJECT_COLOR] = color
    return n

def make_connector(name, pos, connector_type="hinge"):
    c = c4d.BaseObject(c4d.Oconnector)
    c.SetName(name)
    c.SetAbsPos(pos)
    type_desc = c4d.DescID(c4d.DescLevel(1000))
    if connector_type.lower() == "hinge":
        c.SetParameter(type_desc, 0, c4d.DESCFLAGS_SET_0)
    elif connector_type.lower() == "spring":
        c.SetParameter(type_desc, 7, c4d.DESCFLAGS_SET_0)
    else:
        c.SetParameter(type_desc, 0, c4d.DESCFLAGS_SET_0)
    return c

def add_rigidbody(obj, dynamic=True):
    tag = c4d.BaseTag(c4d.Trigidbody)
    state = c4d.RIGID_BODY_DYNAMIC_ON if dynamic else c4d.RIGID_BODY_DYNAMIC_OFF
    tag.SetParameter(c4d.DescID(c4d.DescLevel(1001)), state, c4d.DESCFLAGS_SET_0)
    obj.InsertTag(tag)
    return tag

# ------------------------------------------------------------
# MAIN BUILD
# ------------------------------------------------------------
def build_vehicle(doc):
    body = find_obj(doc, "Body")
    if not body:
        raise Exception("Missing Body object")

    rig_root = make_null("Vehicle_Rig", c4d.Vector(1, 1, 0))
    doc.InsertObject(rig_root)

    # Ground collider
    ground = find_obj(doc, "Ground")
    if ground:
        add_rigidbody(ground, False)

    # Controls
    ctrl = make_null("Controls", c4d.Vector(1, 1, 0))
    ctrl.InsertUnder(rig_root)

    def add_user(ctrl, name, v, minv, maxv, step=1.0):
        bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
        bc[c4d.DESC_NAME] = name
        bc[c4d.DESC_UNIT] = c4d.DESC_UNIT_FLOAT
        bc[c4d.DESC_MIN] = minv
        bc[c4d.DESC_MAX] = maxv
        bc[c4d.DESC_STEP] = step
        element = ctrl.AddUserData(bc)
        ctrl[element] = v
        return element

    speed_id = add_user(ctrl, "MotorSpeed", 0.0, -50, 50)
    steer_id = add_user(ctrl, "SteerAngle", 0.0, -35, 35)
    torque_id = add_user(ctrl, "MotorTorque", 50.0, 0, 500)
    fric_id = add_user(ctrl, "Friction", 1.0, 0, 5)
    stiff_id = add_user(ctrl, "SuspensionStiffness", 4.0, 1, 10)
    damp_id = add_user(ctrl, "SuspensionDamping", 20.0, 0, 100)

    axle_colors = {
        "Front": c4d.Vector(0, 0, 1),
        "Mid": c4d.Vector(0, 1, 0),
        "Rear": c4d.Vector(1, 0, 0)
    }
    wheel_objs = {k: find_obj(doc, f"Wheel_{k}") for k in WHEEL_NAMES}

    for axle_name, keys in AXLES.items():
        axle_null = make_null(f"Axle_{axle_name}", axle_colors[axle_name])
        axle_null.InsertUnder(rig_root)

        for key in keys:
            wheel = wheel_objs.get(key)
            if not wheel:
                continue
            pos = wheel.GetAbsPos()

            # Top cube (anchor)
            top = c4d.BaseObject(c4d.Ocube)
            top.SetName(f"top-{key}")
            top.SetAbsPos(pos + c4d.Vector(0, 150, 0))
            top.SetAbsScale(c4d.Vector(0.3, 0.3, 0.3))
            top.InsertUnder(axle_null)
            add_rigidbody(top, False)

            # Suspension
            susp = make_connector(f"connectSusp-{key}", pos, "spring")
            susp.InsertUnder(axle_null)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10001)), top, c4d.DESCFLAGS_SET_0)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10002)), wheel, c4d.DESCFLAGS_SET_0)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10003)), SUSP_LOWER, c4d.DESCFLAGS_SET_0)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10004)), SUSP_UPPER, c4d.DESCFLAGS_SET_0)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10005)), SUSP_STIFF, c4d.DESCFLAGS_SET_0)
            susp.SetParameter(c4d.DescID(c4d.DescLevel(10006)), SUSP_DAMP, c4d.DESCFLAGS_SET_0)

            # Hinge
            hinge = make_connector(f"connectHinge-{key}", pos, "hinge")
            hinge.InsertUnder(axle_null)
            hinge.SetParameter(c4d.DescID(c4d.DescLevel(10001)), top, c4d.DESCFLAGS_SET_0)
            hinge.SetParameter(c4d.DescID(c4d.DescLevel(10002)), wheel, c4d.DESCFLAGS_SET_0)
            hinge.SetParameter(c4d.DescID(c4d.DescLevel(10010)), True, c4d.DESCFLAGS_SET_0)
            hinge.SetParameter(c4d.DescID(c4d.DescLevel(10011)), MOTOR_SPEED, c4d.DESCFLAGS_SET_0)
            hinge.SetParameter(c4d.DescID(c4d.DescLevel(10012)), MOTOR_TORQUE, c4d.DESCFLAGS_SET_0)

            add_rigidbody(wheel, True)

    # Python tag for motor + steering
    py = c4d.BaseTag(c4d.Tpython)
    py.SetName("MotorDrive")

    code = f"""
import c4d, math
def main():
    ctrl = op.GetObject()
    if not ctrl: return
    rig = ctrl.GetUp()
    if not rig: return
    speed = ctrl[c4d.ID_USERDATA,{speed_id[1].id}]
    torque = ctrl[c4d.ID_USERDATA,{torque_id[1].id}]
    steer = math.radians(ctrl[c4d.ID_USERDATA,{steer_id[1].id}])
    for axle in rig.GetChildren():
        for c in axle.GetChildren():
            if 'connectHinge' in c.GetName():
                c.SetParameter(c4d.DescID(c4d.DescLevel(10010)), True, c4d.DESCFLAGS_SET_0)
                c.SetParameter(c4d.DescID(c4d.DescLevel(10011)), speed, c4d.DESCFLAGS_SET_0)
                c.SetParameter(c4d.DescID(c4d.DescLevel(10012)), torque, c4d.DESCFLAGS_SET_0)
        if axle.GetName() == 'Axle_Front':
            for key in ['Wheel_FL','Wheel_FR']:
                w = doc.SearchObject(key)
                if w: w.SetRelRot(c4d.Vector(0, steer, 0))
    """

    py[c4d.TPYTHON_CODE] = code
    ctrl.InsertTag(py)

    c4d.EventAdd()
    print("✅ Vehicle rig (v14B Unified FIX2) generated — fully dynamic with motor and steering controls.")

# ------------------------------------------------------------
def main():
    doc = c4d.documents.GetActiveDocument()
    build_vehicle(doc)

if __name__ == '__main__':
    main()
