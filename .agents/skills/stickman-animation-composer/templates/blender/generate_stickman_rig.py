"""
Headless Blender Python Script: 3D Procedural Stickman Rig & Render (EEVEE).
Generates an armature skeleton, builds neon cylinder limbs, applies procedural walk/gesture keyframes,
and renders to MP4 or PNG sequence.

Usage:
  blender --background --python generate_stickman_rig.py -- [output_path] [animation_type]
"""

import bpy
import math
import sys
from pathlib import Path


def setup_scene(resolution_x=1080, resolution_y=1920, fps=30, total_frames=90):
    """Sets up clean Blender scene, dimensions, and EEVEE renderer."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngine') else 'BLENDER_EEVEE'
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Dark background
    world = bpy.data.worlds.new("World_Dark")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.04, 0.04, 0.07, 1.0)
        bg_node.inputs['Strength'].default_value = 0.5

    # Camera
    cam_data = bpy.data.cameras.new("StickmanCam")
    cam_obj = bpy.data.objects.new("StickmanCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, -4.5, 1.2)
    cam_obj.rotation_euler = (math.radians(82), 0, 0)

    # Key light
    light_data = bpy.data.lights.new(name="KeyLight", type='POINT')
    light_data.energy = 80.0
    light_data.color = (0.2, 0.9, 1.0)
    light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = (2, -2, 3)

    return scene


def build_neon_material(name="NeonCyan", color=(0.0, 1.0, 0.9, 1.0), emission_strength=5.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = emission_strength

    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    return mat


def create_stickman_rig():
    """Generates complete bone skeleton for Stickman."""
    armature_data = bpy.data.armatures.new("StickmanArmature")
    armature_obj = bpy.data.objects.new("StickmanRig", armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edits = armature_data.edit_bones

    # Hips / Root
    hips = edits.new('Hips')
    hips.head = (0, 0, 1.0)
    hips.tail = (0, 0, 1.3)

    # Spine
    spine = edits.new('Spine')
    spine.head = hips.tail
    spine.tail = (0, 0, 1.8)
    spine.parent = hips

    # Head
    head = edits.new('Head')
    head.head = spine.tail
    head.tail = (0, 0, 2.3)
    head.parent = spine

    # Left Arm
    l_arm = edits.new('UpperArm.L')
    l_arm.head = (0.1, 0, 1.75)
    l_arm.tail = (0.5, 0, 1.45)
    l_arm.parent = spine

    l_forearm = edits.new('Forearm.L')
    l_forearm.head = l_arm.tail
    l_forearm.tail = (0.8, 0, 1.15)
    l_forearm.parent = l_arm

    # Right Arm
    r_arm = edits.new('UpperArm.R')
    r_arm.head = (-0.1, 0, 1.75)
    r_arm.tail = (-0.5, 0, 1.45)
    r_arm.parent = spine

    r_forearm = edits.new('Forearm.R')
    r_forearm.head = r_arm.tail
    r_forearm.tail = (-0.8, 0, 1.15)
    r_forearm.parent = r_arm

    # Left Leg
    l_thigh = edits.new('Thigh.L')
    l_thigh.head = (0.15, 0, 1.0)
    l_thigh.tail = (0.2, 0, 0.5)
    l_thigh.parent = hips

    l_shin = edits.new('Shin.L')
    l_shin.head = l_thigh.tail
    l_shin.tail = (0.2, 0, 0.05)
    l_shin.parent = l_thigh

    # Right Leg
    r_thigh = edits.new('Thigh.R')
    r_thigh.head = (-0.15, 0, 1.0)
    r_thigh.tail = (-0.2, 0, 0.5)
    r_thigh.parent = hips

    r_shin = edits.new('Shin.R')
    r_shin.head = r_thigh.tail
    r_shin.tail = (-0.2, 0, 0.05)
    r_shin.parent = r_thigh

    bpy.ops.object.mode_set(mode='OBJECT')

    # Add 3D Head Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 2.05))
    head_mesh = bpy.context.active_object
    head_mesh.name = "Stickman_Head"
    mat = build_neon_material("HeadNeon", color=(0.2, 1.0, 0.8, 1.0), emission_strength=4.0)
    head_mesh.data.materials.append(mat)

    # Parent Head mesh to Head bone
    head_mesh.parent = armature_obj
    head_mesh.parent_type = 'BONE'
    head_mesh.parent_bone = 'Head'

    return armature_obj


def animate_procedural_walk(armature_obj, total_frames=90, fps=30):
    """Applies procedural gait cycle keyframes."""
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = armature_obj.pose.bones

    scene = bpy.context.scene
    speed = 2.0  # strides/sec

    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        t = (frame / fps) * speed * (2 * math.pi)

        # Leg strides
        if 'Thigh.L' in pose_bones:
            pose_bones['Thigh.L'].rotation_mode = 'XYZ'
            pose_bones['Thigh.L'].rotation_euler[0] = math.sin(t) * 0.5
            pose_bones['Thigh.L'].keyframe_insert(data_path="rotation_euler", frame=frame)

        if 'Thigh.R' in pose_bones:
            pose_bones['Thigh.R'].rotation_mode = 'XYZ'
            pose_bones['Thigh.R'].rotation_euler[0] = math.sin(t + math.pi) * 0.5
            pose_bones['Thigh.R'].keyframe_insert(data_path="rotation_euler", frame=frame)

        # Knee bend
        if 'Shin.L' in pose_bones:
            pose_bones['Shin.L'].rotation_mode = 'XYZ'
            pose_bones['Shin.L'].rotation_euler[0] = max(0, -math.sin(t) * 0.6)
            pose_bones['Shin.L'].keyframe_insert(data_path="rotation_euler", frame=frame)

        # Arms swing opposite
        if 'UpperArm.L' in pose_bones:
            pose_bones['UpperArm.L'].rotation_mode = 'XYZ'
            pose_bones['UpperArm.L'].rotation_euler[0] = -math.sin(t) * 0.45
            pose_bones['UpperArm.L'].keyframe_insert(data_path="rotation_euler", frame=frame)

        if 'UpperArm.R' in pose_bones:
            pose_bones['UpperArm.R'].rotation_mode = 'XYZ'
            pose_bones['UpperArm.R'].rotation_euler[0] = -math.sin(t + math.pi) * 0.45
            pose_bones['UpperArm.R'].keyframe_insert(data_path="rotation_euler", frame=frame)

        # Hip vertical bounce
        if 'Hips' in pose_bones:
            pose_bones['Hips'].location.z = math.sin(t * 2) * 0.05
            pose_bones['Hips'].keyframe_insert(data_path="location", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    print("[Stickman] Procedural animation keyframed successfully.")


if __name__ == "__main__":
    out_file = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1].endswith(".mp4") else "output/video/stickman_blender.mp4"
    scene = setup_scene(1080, 1920, 30, 90)
    arm = create_stickman_rig()
    animate_procedural_walk(arm, 90, 30)

    # Render setup
    scene.render.filepath = out_file
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'

    print(f"[Stickman] Ready to render to {out_file}")
    # bpy.ops.render.render(animation=True)
