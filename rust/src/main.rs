#![warn(rust_2018_idioms)]

use std::env;
use std::time::Duration;

use ggez::conf;
use ggez::event;
use ggez::graphics;
use ggez::timer;
use ggez::{Context, GameResult};

use openmoonstone::game::Game;
use openmoonstone::input;
use openmoonstone::scenes;
use openmoonstone::scenes::{EncounterScene, FSceneStack, Fade, Menu};
use openmoonstone::scenes::transition::FadeStyle;

struct MainState {
    input_binding: input::InputBinding,
    scene_stack: FSceneStack,
}

impl event::EventHandler for MainState {
    fn update(&mut self, ctx: &mut Context) -> GameResult<()> {
        const DESIRED_FPS: u32 = 1000 / (1193182 / 21845 * 2);
        // const DESIRED_FPS: u32 = 1;
        while timer::check_update_time(ctx, DESIRED_FPS) {
            let delta = timer::get_delta(ctx);
            // println!("delta main {:?}", delta);
            self.scene_stack
                .world
                .input
                .update(delta.as_secs() as f32 + delta.subsec_millis() as f32 / 1000.0);
            self.scene_stack.update();
            timer::sleep(Duration::from_millis(50));
        }
        Ok(())
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        self.scene_stack.draw(ctx);
        graphics::present(ctx);
        Ok(())
    }

    fn key_down_event(
        &mut self,
        _ctx: &mut Context,
        keycode: event::Keycode,
        _keymod: event::Mod,
        _repeat: bool,
    ) {
        if let Some(ev) = self.input_binding.resolve(keycode) {
            self.scene_stack.input(ev, true);
            self.scene_stack.world.input.update_effect(ev, true);
        }
    }

    fn key_up_event(
        &mut self,
        _ctx: &mut Context,
        keycode: event::Keycode,
        _keymod: event::Mod,
        _repeat: bool,
    ) {
        if let Some(ev) = self.input_binding.resolve(keycode) {
            self.scene_stack.input(ev, false);
            self.scene_stack.world.input.update_effect(ev, false);
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let filename = &args[1];

    let c = conf::Conf::new();
    let ctx = &mut Context::load_from_conf("openmoonstone", "joetsoi", c).unwrap();
    graphics::set_default_filter(ctx, graphics::FilterMode::Nearest);

    let game = Game::new().expect("failed to initialize game");
    let mut scene_stack = scenes::FSceneStack::new(ctx, game);

    let encounter_scene = EncounterScene::new(
        ctx,
        &mut scene_stack.world.store,
        &["knight", "dagger"],
        filename,
    )
    .expect("failed to init game");
    scene_stack.push(Box::new(encounter_scene));

    let fade_in = Fade::new(274, 1, FadeStyle::In);
    scene_stack.push(Box::new(fade_in));
    let fade_out = Fade::new(274, 1, FadeStyle::Out);
    scene_stack.push(Box::new(fade_out));

    let menu = Menu::new(ctx, &mut scene_stack.world.store).unwrap();
    scene_stack.push(Box::new(menu));

    let fade_in = Fade::new(274, 5, FadeStyle::In);
    scene_stack.push(Box::new(fade_in));

    let mut state = MainState {
        scene_stack,
        input_binding: input::create_input_binding(),
    };

    event::run(ctx, &mut state).unwrap();;
}
