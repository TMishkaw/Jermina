---
name: blender-render-automation
description: >-
  Headless 3D motion graphics and cinematic rendering using Python and Blender API (bpy).
  Generates automated Python scripts to clean scenes, import models (e.g. germina_blueprint_head.obj),
  build procedural shaders (cyberpunk neon, wireframe sweep, metallic glass), animate camera rigs,
  and render frames/video in headless mode using EEVEE or Cycles with GPU acceleration.
---

# Blender Render Automation Skill

## Overview
This skill executes **headless 3D motion design and rendering** using Blender's Python API (`bpy`).
It enables autonomous generation and execution of Python scripts that set up scenes, import geometry, build procedural shader node trees, animate cinematic camera movements, and render PNG sequences or MP4 videos without opening the Blender GUI.

---

## 1. Headless Architecture & CLI Execution

### Running Blender in Background Mode
```bash
# Render animation defined in script
blender -b --python script_render_animation.py

# Render with specific output path and frame range
blender -b --python script_render_animation.py -- -s 1 -e 120 -o //out/render_
```

---

## 2. Standard Scene Setup Script Template (`render_pipeline.py`)

This template automatically:
1. Cleans factory cubes/lamps.
2. Configures GPU rendering (Cycles or EEVEE Next).
3. Sets 9:16 vertical resolution (1080x1920, 60fps).
4. Imports OBJ (`germina_blueprint_head.obj`).
5. Creates a Cyberpunk Neon Wireframe / Fresnel Shader.
6. Rig-animates the camera in a 360° orbit.
7. Renders the output.

```python
import bpy
import math
import os

def setup_scene(resolution_x=1080, resolution_y=1920, fps=60, total_frames=180):
    # 1. Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' # or 'CYCLES'
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = total_frames
    
    # Transparent background (useful for compositing over Remotion/Web)
    scene.render.film_transparent = True
    
    # GPU Acceleration if available
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX' # or 'CUDA'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = True
        scene.cycles.device = 'GPU'
    except Exception:
        pass
    
    return scene

def import_model(obj_path):
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"Model file not found: {obj_path}")
    
    bpy.ops.wm.obj_import(filepath=obj_path)
    imported_objects = bpy.context.selected_objects
    
    # Join into a single mesh if multiple parts
    if imported_objects:
        bpy.context.view_layer.objects.active = imported_objects[0]
        bpy.ops.object.join()
        obj = bpy.context.active_object
        
        # Center origin to geometry
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        obj.location = (0, 0, 0)
        return obj
    return None

def apply_cyber_shader(target_obj, neon_color=(0.0, 0.94, 1.0, 1.0)):
    # Create Material
    mat = bpy.data.materials.new(name="CyberHologram")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Create shader nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (100, 0)
    principled.inputs['Base Color'].default_value = (0.02, 0.04, 0.08, 1.0)
    principled.inputs['Metallic'].default_value = 0.95
    principled.inputs['Roughness'].default_value = 0.15
    principled.inputs['Emission Color'].default_value = neon_color
    principled.inputs['Emission Strength'].default_value = 3.5

    # Wireframe overlay node
    wireframe = nodes.new(type='ShaderNodeWireframe')
    wireframe.location = (-200, 100)
    wireframe.inputs['Size'].default_value = 0.004
    wireframe.use_pixel_size = False

    # Mix shader between base metallic and glowing wireframe
    mix = nodes.new(type='ShaderNodeMixShader')
    mix.location = (250, 0)
    
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 150)
    emission.inputs['Color'].default_value = neon_color
    emission.inputs['Strength'].default_value = 5.0

    links.new(wireframe.outputs['Fac'], mix.inputs['Fac'])
    links.new(principled.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output_node.inputs['Surface'])

    # Assign to object
    target_obj.data.materials.clear()
    target_obj.data.materials.append(mat)

def setup_camera_and_lights(target_obj, total_frames=180):
    # Camera
    cam_data = bpy.data.cameras.new(name="CinematicCam")
    cam_obj = bpy.data.objects.new("CinematicCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    cam_data.lens = 50 # 50mm cinematic lens

    # Camera Orbit Animation
    radius = 2.8
    height = 0.2
    for frame in range(1, total_frames + 1):
        angle = (frame / total_frames) * 2 * math.pi
        cam_obj.location.x = radius * math.cos(angle)
        cam_obj.location.y = radius * math.sin(angle)
        cam_obj.location.z = height + 0.1 * math.sin(angle * 2)
        
        # Track to center
        dx = -cam_obj.location.x
        dy = -cam_obj.location.y
        dz = -cam_obj.location.z
        rot_z = math.atan2(dy, dx) - math.pi / 2
        cam_obj.rotation_euler = (math.radians(85), 0, rot_z)
        
        cam_obj.keyframe_insert(data_path="location", frame=frame)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Key Light (Cyan)
    light_data = bpy.data.lights.new(name="KeyLight", type='POINT')
    light_data.energy = 300
    light_data.color = (0.0, 0.8, 1.0)
    light_obj = bpy.data.objects.new("KeyLight", light_data)
    light_obj.location = (2, -2, 3)
    bpy.context.collection.objects.link(light_obj)

    # Rim Light (Magenta/Orange)
    rim_data = bpy.data.lights.new(name="RimLight", type='POINT')
    rim_data.energy = 500
    rim_data.color = (1.0, 0.05, 0.5)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (-2.5, 2.5, -0.5)
    bpy.context.collection.objects.link(rim_obj)

def run():
    model_path = r"D:\JERMINA\germina_blueprint_head.obj"
    out_dir = r"D:\JERMINA\renders\blender_out"
    os.makedirs(out_dir, exist_ok=True)
    
    scene = setup_scene(resolution_x=1080, resolution_y=1920, fps=60, total_frames=180)
    scene.render.filepath = os.path.join(out_dir, "frame_####")
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    
    model = import_model(model_path)
    if model:
        apply_cyber_shader(model)
        setup_camera_and_lights(model, total_frames=180)
        
        # Start render animation
        bpy.ops.render.render(animation=True)
        print("Render finished successfully!")

if __name__ == "__main__":
    run()
```
