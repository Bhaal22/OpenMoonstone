use ggez::graphics::DrawMode;
use ggez::{graphics, Context, GameResult};
use ggez_goodies::scene::{Scene, SceneSwitch};

use crate::game::{Game, SceneState};
use crate::input::{Axis, Button, InputEvent};
use crate::scenes::FSceneSwitch;

use super::transition::FadeStyle;
use super::{EncounterScene, Fade};
/// Scene that controls switching between various game states.
///
/// Base state that switches between the menu, practice encounter and
/// other game states, draws a black screen that allows the fade in and fade out
/// to work.
///
/// We need this as the current ggez scene stack requires a scene. The other
/// option would be to change the scene stack to not have `expects()` and raise
/// and option instead and use None to handle scene transitions.
pub struct MainScene {}

impl MainScene {
    pub fn new() -> Self {
        Self {}
    }
}

impl Scene<Game, InputEvent> for MainScene {
    fn update(&mut self, game: &mut Game, ctx: &mut Context) -> FSceneSwitch {
        match game.scene {
            SceneState::Menu => {
                let encounter_scene = Box::new(
                    EncounterScene::new(ctx, &mut game.store, &["knight", "dagger"], "wab1")
                        .expect("failed to init practice encounter"),
                );

                match game.next_scene {
                    SceneState::Practice => SceneSwitch::PushMultiple(vec![
                        encounter_scene,
                        Box::new(Fade::new(274, 1, FadeStyle::In)),
                    ]),
                    _ => SceneSwitch::None,
                }
            }
            _ => SceneSwitch::None,
        }
    }

    fn draw(&mut self, game: &mut Game, ctx: &mut Context) -> GameResult<()> {
        graphics::set_color(ctx, graphics::Color::new(0.0, 0.0, 0.0, 1.0))?;
        graphics::rectangle(
            ctx,
            DrawMode::Fill,
            graphics::Rect {
                x: 0.0,
                y: 0.0,
                //TODO: handle scale factor
                w: 320.0 * 3.0,
                h: 200.0 * 3.0,
            },
        );
        graphics::set_color(ctx, graphics::Color::new(1.0, 1.0, 1.0, 1.0))?;
        Ok(())
    }

    fn name(&self) -> &str {
        "Main"
    }

    fn input(&mut self, _gameworld: &mut Game, _event: InputEvent, _started: bool) {}
}